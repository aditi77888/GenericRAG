from abc import ABC, abstractmethod


class BaseAgent(ABC):

    @abstractmethod
    def handle(self, query: str) -> str:
        """
        Handle a user query and return a response.
        """
        pass