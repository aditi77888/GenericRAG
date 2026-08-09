from sentence_transformers import SentenceTransformer

from embeddings.base_embedding import BaseEmbedding
from models.chunk import Chunk


class QwenEmbedding(BaseEmbedding):
    """
    Embedding model using Qwen3-Embedding-0.6B.
    """

    def __init__(
            self,
            model_name: str = "Qwen/Qwen3-Embedding-0.6B"
    ):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(
            self,
            chunks: list[Chunk]
    ):
        """
        Generate embeddings for document chunks.

        Args:
            chunks: List of Chunk objects.

        Returns:
            numpy.ndarray of shape (num_chunks, embedding_dimension)
        """

        if not chunks:
            return []

        texts = [chunk.content for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            batch_size=16,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False
        )

        return embeddings

    def embed_query(
            self,
            query: str
    ):
        """
        Generate embedding for a user query.

        Args:
            query: User query.

        Returns:
            numpy.ndarray of shape (embedding_dimension,)
        """

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding