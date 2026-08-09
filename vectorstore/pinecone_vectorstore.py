import hashlib
import os

from dotenv import load_dotenv
from pinecone import Pinecone

from models.chunk import Chunk
from vectorstore.base_vectorstore import BaseVectorStore


class PineconeVectorStore(BaseVectorStore):

    def __init__(self):

        load_dotenv()

        api_key = os.getenv(
            "PINECONE_API_KEY"
        )

        index_name = os.getenv(
            "PINECONE_INDEX_NAME"
        )

        if not api_key:
            raise ValueError(
                "PINECONE_API_KEY is not set."
            )

        if not index_name:
            raise ValueError(
                "PINECONE_INDEX_NAME is not set."
            )

        self.pc = Pinecone(
            api_key=api_key
        )

        self.index = self.pc.Index(
            index_name
        )

    def add(
            self,
            chunks,
            embeddings,
            namespace="default"
    ):

        print(
            f"[PINECONE] Preparing {len(chunks)} vectors...",
            flush=True
        )

        vectors = []

        for i, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
        ):

            print(
                f"[PINECONE] Processing vector "
                f"{i + 1}/{len(chunks)}...",
                flush=True
            )

            print(
                f"  - chunk type: {type(chunk)}",
                flush=True
            )

            print(
                f"  - embedding type: {type(embedding)}",
                flush=True
            )

            print(
                f"  - embedding shape: {embedding.shape}",
                flush=True
            )

            print(
                f"  - metadata keys: "
                f"{list(chunk.metadata.keys())}",
                flush=True
            )

            # ---------------------------------------
            # GET SOURCE
            # ---------------------------------------

            source = str(
                chunk.metadata.get(
                    "source",
                    "unknown"
                )
            )

            # ---------------------------------------
            # GET FILE NAME
            # ---------------------------------------

            file_name = chunk.metadata.get(
                "file_name"
            )

            if not file_name:
                file_name = os.path.basename(
                    source
                )

            # ---------------------------------------
            # GET CHUNK ID
            # ---------------------------------------

            chunk_id = chunk.metadata.get(
                "chunk_id",
                i
            )

            # ---------------------------------------
            # NORMALIZE METADATA
            # ---------------------------------------

            metadata = {
                **chunk.metadata,

                # Make sure every document has
                # a consistent file_name field.
                "file_name": file_name,

                "text": chunk.content
            }

            # ---------------------------------------
            # CREATE VECTOR ID
            # ---------------------------------------

            vector_id = hashlib.md5(
                f"{source}_{chunk_id}".encode()
            ).hexdigest()

            print(
                f"  - vector id: {vector_id}",
                flush=True
            )

            # ---------------------------------------
            # CREATE VECTOR
            # ---------------------------------------

            vectors.append(
                {
                    "id": vector_id,

                    "values": embedding.tolist(),

                    "metadata": metadata
                }
            )

            print(
                f"  - vector {i + 1} created",
                flush=True
            )

        print(
            "[PINECONE] Finished constructing vectors.",
            flush=True
        )

        print(
            "[PINECONE] Calling upsert...",
            flush=True
        )

        result = self.index.upsert(
            vectors=vectors,
            namespace=namespace
        )

        print(
            "[PINECONE] Upsert returned!",
            flush=True
        )

        print(
            f"[PINECONE] Response: {result}",
            flush=True
        )

        return result

    def search(
            self,
            query_embedding,
            top_k: int = 5,
            namespace: str = "default"
    ):

        results = self.index.query(

            vector=query_embedding.tolist(),

            top_k=top_k,

            include_metadata=True,

            namespace=namespace
        )

        chunks = []

        for match in results.matches:

            metadata = dict(
                match.metadata
            )

            metadata["score"] = match.score

            text = metadata.pop(
                "text",
                ""
            )

            chunks.append(
                Chunk(
                    content=text,
                    metadata=metadata
                )
            )

        return chunks

    def delete_namespace(
            self,
            namespace: str
    ):

        try:

            self.index.delete(
                delete_all=True,
                namespace=namespace
            )

        except Exception as e:

            # Namespace may not exist yet.
            if "Namespace not found" in str(e):
                return

            raise