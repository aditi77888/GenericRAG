from abc import ABC, abstractmethod


class BaseParser(ABC):

    @abstractmethod
    def parse(self, source):
        """
        Parse a document and return
        a list of Document objects.
        """
        pass