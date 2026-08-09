from llms.base_llm import BaseLLM
from llms.gemini_llm import GeminiLLM
from llms.groq_llm import GroqLLM


class FallbackLLM(BaseLLM):

    def __init__(
        self,
        primary_model="gemini-3.6-flash",
        fallback_model="llama-3.3-70b-versatile"
    ):

        self.primary = GeminiLLM(
            primary_model
        )

        self.fallback = GroqLLM(
            fallback_model
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0,
        max_tokens: int = 1024
    ) -> str:

        # =====================================================
        # PRIMARY → GEMINI
        # =====================================================

        try:

            print(
                "[LLM] Trying Gemini...",
                flush=True
            )

            response = self.primary.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )

            print(
                "[LLM] Gemini succeeded.",
                flush=True
            )

            return response

        # =====================================================
        # FALLBACK → GROQ / LLAMA
        # =====================================================

        except Exception as e:

            print(
                "[LLM] Gemini failed:",
                repr(e),
                flush=True
            )

            print(
                "[LLM] Falling back to Groq / Llama...",
                flush=True
            )

            try:

                response = self.fallback.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                print(
                    "[LLM] Groq / Llama succeeded.",
                    flush=True
                )

                return response

            except Exception as fallback_error:

                print(
                    "[LLM] Groq / Llama also failed:",
                    repr(fallback_error),
                    flush=True
                )

                raise RuntimeError(
                    "Both Gemini and Groq/Llama failed."
                ) from fallback_error