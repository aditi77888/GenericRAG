from abc import ABC, abstractmethod
from typing import List
from models.document import Document
class BaseLoader(ABC):

    @abstractmethod
    def load(self, source)-> List[Document]:
        """
        Reads the input source and returns one or more Document object.

        """
        pass