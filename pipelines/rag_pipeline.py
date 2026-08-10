from pathlib import Path

from chunkers.base_chunker import BaseChunker
from embeddings.base_embedding import BaseEmbedding
from llms.base_llm import BaseLLM

import uuid

from loaders.loader_factory import LoaderFactory
from parsers.parser_factory import ParserFactory

from prompts.prompt_builder import PromptBuilder

from retriever.base_retriever import BaseRetriever
from vectorstore.base_vectorstore import BaseVectorStore
import re

class RAGPipeline:

    def __init__(
            self,
            chunker: BaseChunker,
            embedding_model: BaseEmbedding,
            vector_store: BaseVectorStore,
            retriever: BaseRetriever,
            llm: BaseLLM,
            prompt_builder: PromptBuilder
    ):

        self.chunker = chunker
        self.embedding_model = embedding_model
        self.vector_store = vector_store
        self.retriever = retriever
        self.llm = llm
        self.prompt_builder = prompt_builder

        # Minimum similarity score required for a chunk
        # to be considered relevant.
        self.retrieval_threshold = 0.40

    # ========================================================
    # INDEX DOCUMENT
    # ========================================================
    #
    # Multiple documents can now share the same namespace
    # (e.g. one namespace per chat session, holding several
    # uploaded PDFs). Every chunk is tagged with document_id
    # and file_name so retrieval results can still be traced
    # back to the exact file they came from.
    # ========================================================

    def index_document(
            self,
            source,
            namespace="default",
            document_id=None,
            file_name=None
    ):

        loader = LoaderFactory.create(source)

        loaded_data = loader.load(source)

        parser = ParserFactory.create(source)

        if parser is None:

            documents = loaded_data

        else:

            documents = parser.parse(
                loaded_data
            )

        # ----------------------------------------------------
        # Tag every document with document_id / file_name
        # ----------------------------------------------------

        for document in documents:

            if document_id is not None:
                document.metadata["document_id"] = document_id

            if file_name is not None:
                document.metadata["file_name"] = file_name

        chunks = self.chunker.chunk(
            documents
        )

        embeddings = self.embedding_model.embed_documents(
            chunks
        )

        self.vector_store.add(
            chunks,
            embeddings,
            namespace
        )

        return len(chunks)

    # ========================================================
    # INGEST
    # ========================================================
    #
    # Ingest ONE document.
    #
    # - If `namespace` is given, the document is added into
    #   that (possibly shared, multi-document) namespace.
    # - If `namespace` is not given, a brand new namespace is
    #   created for this document alone (legacy single-doc
    #   behaviour, kept for backward compatibility).
    # ========================================================

    def ingest(
            self,
            source,
            namespace=None,
            document_id=None,
            file_name=None
    ):
        """
        Ingest a document into the vector store.

        Returns:
            dict: {
                "document_id": str,
                "namespace": str,
                "file_name": str,
                "chunk_count": int
            }
        """

        if document_id is None:
            document_id = uuid.uuid4().hex

        if namespace is None:
            namespace = f"document_{document_id}"

        if file_name is None:
            file_name = Path(source).name

        chunk_count = self.index_document(
            source=source,
            namespace=namespace,
            document_id=document_id,
            file_name=file_name
        )

        return {
            "document_id": document_id,
            "namespace": namespace,
            "file_name": file_name,
            "chunk_count": chunk_count
        }

    # ========================================================
    # INDEX MULTIPLE DOCUMENTS (kept for backward compatibility)
    # ========================================================

    def index_documents(
            self,
            sources: list[str],
            namespace="default"
    ):

        total_chunks = 0

        for source in sources:

            total_chunks += self.index_document(
                source,
                namespace
            )

        return total_chunks

    # ========================================================
    # ASK
    # ========================================================

    def ask(
            self,
            question,
            document_id=None,
            namespace=None,
            chat_history=None,
            top_k=5
    ):

        if document_id is not None:
            namespace = f"document_{document_id}"

        elif namespace is None:
            namespace = "default"

        print(
            f"[RAG PIPELINE] Question: {question}",
            flush=True
        )

        print(
            f"[RAG PIPELINE] Namespace: {namespace}",
            flush=True
        )

        # ====================================================
        # BUILD RETRIEVAL QUERY
        #
        # Fold recent chat history into the query used for
        # embedding/search, so follow-up questions that rely
        # on earlier context ("what about his email?") can
        # still retrieve the right chunks. The ORIGINAL
        # question (not this expanded version) is what gets
        # shown to the answering LLM as "USER QUESTION".
        # ====================================================

        retrieval_query = question

        if chat_history:
            retrieval_query = f"{chat_history}\nUser: {question}"

        chunks = self.retriever.retrieve(

            query=retrieval_query,

            top_k=top_k,

            namespace=namespace
        )

        print(
            f"[RAG PIPELINE] Retrieved {len(chunks)} chunks.",
            flush=True
        )

        relevant_chunks = []

        for chunk in chunks:

            score = chunk.metadata.get(
                "score",
                0
            )

            print(
                f"[RAG PIPELINE] Chunk score: {score} "
                f"(file: {chunk.metadata.get('file_name', '?')})",
                flush=True
            )

            if score >= self.retrieval_threshold:

                relevant_chunks.append(
                    chunk
                )

        print(
            f"[RAG PIPELINE] Relevant chunks: "
            f"{len(relevant_chunks)}",
            flush=True
        )

        if not relevant_chunks:

            print(
                "[RAG PIPELINE] No relevant chunks found.",
                flush=True
            )

            return {
                "answer": (
                    "I couldn't find relevant information "
                    "in the uploaded document(s) to answer "
                    "this question."
                ),

                "chunks": [],

                "sources": []
            }

        prompt = self.prompt_builder.build(

            question=question,

            chunks=relevant_chunks,

            chat_history=chat_history
        )

        print(
            "[RAG PIPELINE] Sending relevant context to LLM...",
            flush=True
        )

        answer = self.llm.generate(
            prompt
        )

        sources = []

        for chunk in relevant_chunks:

            metadata = chunk.metadata

            file_label = metadata.get(
                "file_name",
                metadata.get(
                    "source",
                    "Unknown source"
                )
            )

            source = (
                f"{file_label}"
                f" (Page {metadata.get('page', '-')})"
            )

            if source not in sources:

                sources.append(
                    source
                )

        return {

            "answer": answer,

            "chunks": relevant_chunks,

            "sources": sources
        }