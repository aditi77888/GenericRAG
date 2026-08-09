from sentence_transformers import SentenceTransformer

from embeddings.base_embedding import BaseEmbedding
from models.chunk import Chunk


class BGEEmbedding(BaseEmbedding):
    """
    Embedding model using BAAI/bge-small-en-v1.5.
    """

    def __init__(
            self,
            model_name: str = "BAAI/bge-small-en-v1.5"
    ):

        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

    def embed_documents(
            self,
            chunks: list[Chunk]
    ):

        if not chunks:
            return []

        texts = [
            chunk.content
            for chunk in chunks
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embeddings

    def embed_query(
            self,
            query: str
    ):

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding