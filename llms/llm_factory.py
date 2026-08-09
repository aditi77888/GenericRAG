from llms.gemini_llm import GeminiLLM
from llms.groq_llm import GroqLLM
from llms.fallback_llm import FallbackLLM


class LLMFactory:

    @staticmethod
    def create(
        llm_name: str = "gemini",
        model_name: str = "gemini-3.6-flash"
    ):

        llm_name = llm_name.lower()

        # =====================================================
        # GEMINI
        # =====================================================

        if llm_name == "gemini":

            return GeminiLLM(
                model_name
            )

        # =====================================================
        # GROQ / LLAMA
        # =====================================================

        if llm_name == "groq":

            return GroqLLM(
                model_name or
                "llama-3.3-70b-versatile"
            )

        # =====================================================
        # GEMINI → GROQ/LLAMA FALLBACK
        # =====================================================

        if llm_name == "fallback":

            return FallbackLLM(
                primary_model="gemini-3.6-flash",
                fallback_model="llama-3.3-70b-versatile"
            )

        raise ValueError(
            f"Unsupported LLM: {llm_name}"
        )