from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(
            self,
            prompt: str,
            temperature: float = 0,
            max_tokens: int = 1024
    ) -> str:
        """
        Generate a response from the LLM.
        """
        pass