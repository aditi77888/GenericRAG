from abc import ABC, abstractmethod


class BaseChunker(ABC):

    @abstractmethod
    def chunk(self, documents):
        """
        Splits documents into chunks.

        Args:
            documents: List[Document]

        Returns:
            List[Chunk]
        """
        pass