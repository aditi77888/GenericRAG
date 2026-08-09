from abc import ABC, abstractmethod


class BaseEmbedding(ABC):

    @abstractmethod
    def embed_documents(self, chunks):
        """
        Convert chunks into embeddings.

        Returns
        -------
        List[List[float]]
        """
        pass

    @abstractmethod
    def embed_query(self, query):
        """
        Convert a query into an embedding.

        Returns
        -------
        List[float]
        """
        pass