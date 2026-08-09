from abc import ABC, abstractmethod

from models.chunk import Chunk


class BaseVectorStore(ABC):

    @abstractmethod
    def add(self, chunks: list[Chunk], embeddings, namespace: str = "default"):
        pass

    @abstractmethod
    def search(self, query_embedding, top_k=5, namespace: str = "default"):
        pass


    @abstractmethod
    def delete_namespace(
            self,
            namespace: str
    ):
        """
        Delete all vectors in a namespace.
        """
        pass