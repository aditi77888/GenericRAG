import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from llms.base_llm import BaseLLM


class GroqLLM(BaseLLM):

    def __init__(
            self,
            model_name="llama-3.3-70b-versatile"
    ):

        load_dotenv()

        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name=model_name,
            temperature=0
        )

    def generate(
            self,
            prompt: str,
            temperature: float = 0,
            max_tokens: int = 1024
    ) -> str:

        self.llm.temperature = temperature
        self.llm.max_tokens = max_tokens

        response = self.llm.invoke(prompt)

        return response.content