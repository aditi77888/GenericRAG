
import os

from dotenv import load_dotenv
from google import genai

from llms.base_llm import BaseLLM


class GeminiLLM(BaseLLM):

    def __init__(
            self,
            model_name: str = "gemini-3.6-flash"
    ):

        load_dotenv()

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model_name = model_name

    def generate(
            self,
            prompt: str,
            temperature: float = 0,
            max_tokens: int = 1024
    ) -> str:

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            }
        )

        print("\nRAW GEMINI RESPONSE:")
        print(response)

        print("\nRESPONSE TEXT:")
        print(repr(response.text))

        return response.text