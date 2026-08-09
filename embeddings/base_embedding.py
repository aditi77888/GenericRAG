from abc import ABC, abstractmethod
import numpy as np



class BaseEmbedding(ABC):

    @abstractmethod
    def embed_documents(
            self,
            chunks: list["Chunk"]
    ) -> np.ndarray:
        pass



    @abstractmethod
    def embed_query(
        self,
        query: str
    )-> np.ndarray:
        """
        Convert a query into an embedding.

        Returns:
            numpy.ndarray
            Shape: (embedding_dimension,)
        """
        pass