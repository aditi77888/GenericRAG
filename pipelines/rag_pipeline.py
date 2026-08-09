from chunkers.base_chunker import BaseChunker
from embeddings.base_embedding import BaseEmbedding
from llms.base_llm import BaseLLM

import uuid

from loaders.loader_factory import LoaderFactory
from parsers.parser_factory import ParserFactory

from prompts.prompt_builder import PromptBuilder

from retriever.base_retriever import BaseRetriever
from vectorstore.base_vectorstore import BaseVectorStore


class RAGPipeline:

    # ========================================================
    # INITIALIZATION
    # ========================================================

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
        self.retrieval_threshold = 0.55

    # ========================================================
    # INDEX DOCUMENT
    # ========================================================

    def index_document(
            self,
            source,
            namespace="default"
    ):

        # ----------------------------------------------------
        # Loader
        # ----------------------------------------------------

        loader = LoaderFactory.create(source)

        loaded_data = loader.load(source)

        # ----------------------------------------------------
        # Parser
        # ----------------------------------------------------

        parser = ParserFactory.create(source)

        if parser is None:

            documents = loaded_data

        else:

            documents = parser.parse(
                loaded_data
            )

        # ----------------------------------------------------
        # Chunking
        # ----------------------------------------------------

        chunks = self.chunker.chunk(
            documents
        )

        # ----------------------------------------------------
        # Embeddings
        # ----------------------------------------------------

        embeddings = self.embedding_model.embed_documents(
            chunks
        )

        # ----------------------------------------------------
        # Vector Store
        # ----------------------------------------------------

        self.vector_store.add(
            chunks,
            embeddings,
            namespace
        )

        return len(chunks)

    # ========================================================
    # INDEX MULTIPLE DOCUMENTS
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
    # INGEST
    # ========================================================

    def ingest(self, source):

        """
        Ingest a document and create a unique namespace.

        Returns:
            str: Unique document ID.
        """

        document_id = uuid.uuid4().hex

        namespace = f"document_{document_id}"

        self.index_document(
            source=source,
            namespace=namespace
        )

        return document_id

    # ========================================================
    # ASK
    # ========================================================

    def ask(
            self,
            question,
            document_id=None,
            namespace=None,
            top_k=5
    ):

        # ----------------------------------------------------
        # Determine namespace
        # ----------------------------------------------------

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
        # RETRIEVAL
        # ====================================================

        chunks = self.retriever.retrieve(

            query=question,

            top_k=top_k,

            namespace=namespace
        )

        print(
            f"[RAG PIPELINE] Retrieved {len(chunks)} chunks.",
            flush=True
        )

        # ====================================================
        # RETRIEVAL CONFIDENCE CHECK
        # ====================================================

        relevant_chunks = []

        for chunk in chunks:

            score = chunk.metadata.get(
                "score",
                0
            )

            print(
                f"[RAG PIPELINE] Chunk score: {score}",
                flush=True
            )

            if score >= 0.40:

                relevant_chunks.append(
                    chunk
                )

        print(
            f"[RAG PIPELINE] Relevant chunks: "
            f"{len(relevant_chunks)}",
            flush=True
        )

        # ====================================================
        # NO RELEVANT INFORMATION
        # ====================================================

        if not relevant_chunks:

            print(
                "[RAG PIPELINE] No relevant chunks found.",
                flush=True
            )

            return {
                "answer": (
                    "I couldn't find relevant information "
                    "in the document to answer this question."
                ),

                "chunks": [],

                "sources": []
            }

        # ====================================================
        # PROMPT
        # ====================================================

        prompt = self.prompt_builder.build(

            question=question,

            chunks=relevant_chunks
        )

        # ====================================================
        # LLM
        # ====================================================

        print(
            "[RAG PIPELINE] Sending relevant context to LLM...",
            flush=True
        )

        answer = self.llm.generate(
            prompt
        )

        # ====================================================
        # SOURCES
        # ====================================================

        sources = []

        for chunk in relevant_chunks:

            metadata = chunk.metadata

            source = (
                f"{metadata.get('source', 'Unknown source')}"
                f" (Page {metadata.get('page', '-')})"
            )

            if source not in sources:

                sources.append(
                    source
                )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "answer": answer,

            "chunks": relevant_chunks,

            "sources": sources
        }