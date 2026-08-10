import json

from agents.base_agent import BaseAgent
from llms.llm_factory import LLMFactory


class AnswerGuardrailAgent(BaseAgent):

    def __init__(self):

        self.llm = LLMFactory.create(
            #llm_name="fallback"
            llm_name="groq",
            model_name="llama-3.3-70b-versatile"
        )

    # =========================================================
    # MAIN
    # =========================================================

    def handle(
        self,
        question: str,
        answer: str,
        chunks: list
    ) -> dict:

        # -----------------------------------------------------
        # No answer
        # -----------------------------------------------------

        if not answer or not answer.strip():

            return {
                "allowed": False,
                "grounded": False,
                "category": "empty_answer",
                "reason": "The generated answer is empty.",
                "answer": (
                    "I couldn't generate a reliable answer "
                    "from the document."
                ),
                "agent": "answer_guardrail"
            }

        # -----------------------------------------------------
        # No retrieved context
        # -----------------------------------------------------

        if not chunks:

            return {
                "allowed": False,
                "grounded": False,
                "category": "no_context",
                "reason": (
                    "No relevant document context was retrieved."
                ),
                "answer": (
                    "I couldn't find enough information "
                    "in the document to answer this question."
                ),
                "agent": "answer_guardrail"
            }

        # =====================================================
        # BUILD CONTEXT
        # =====================================================
        # =====================================================
        # BUILD CONTEXT
        # =====================================================

        context_parts = []

        for i, chunk in enumerate(chunks, start=1):
            metadata = chunk.metadata or {}

            file_name = metadata.get(
                "file_name",
                metadata.get("source", "Unknown")
            )

            page = metadata.get(
                "page",
                "Unknown"
            )

            context_parts.append(
                f"""
        --- CONTEXT CHUNK {i} ---
        FILE: {file_name}
        PAGE: {page}

        CONTENT:
        {chunk.content}

        --- END CHUNK {i} ---
        """
            )

        context = "\n".join(context_parts)

        print(
            "\n[ANSWER GUARDRAIL] CONTEXT SENT FOR VALIDATION:",
            flush=True
        )

        print(
            context,
            flush=True
        )

        # =====================================================
        # VALIDATION PROMPT
        # =====================================================

        prompt = f"""
        You are an Answer Validation Guardrail for a RAG system.

        Your ONLY job is to determine whether the generated answer
        is supported by the retrieved document context.

        USER QUESTION:
        {question}

        RETRIEVED DOCUMENT CONTEXT:
        {context}

        GENERATED ANSWER:
        {answer}

        Rules:

        1. The answer must be supported by the CONTENT or METADATA.
        2. PAGE metadata is authoritative for page-related questions.
        3. FILE metadata is authoritative for file-related questions.
        4. If the answer correctly states information contained
           in the retrieved content, it is grounded.
        5. Do not require the words "page 1", "page 2", etc. to
           literally appear inside the OCR text when PAGE metadata
           identifies the page.
        6. If the answer says information is unavailable, only mark
           it relevant if the requested information truly cannot
           be obtained from the provided context.
        7. Do not use outside knowledge.

        Return ONLY valid JSON:

        {{
            "grounded": true or false,
            "relevant": true or false,
            "hallucination": true or false,
            "category": "grounded" or "unsupported_claim" or
                         "hallucination" or "irrelevant",
            "reason": "short explanation"
        }}
        """

        # =====================================================
        # CALL VALIDATION LLM
        # =====================================================

        response = self.llm.generate(
            prompt
        )

        print(
            "\n[ANSWER GUARDRAIL] RAW RESPONSE:",
            flush=True
        )

        print(
            response,
            flush=True
        )

        # =====================================================
        # PARSE RESULT
        # =====================================================

        validation = self._parse_response(
            response
        )

        # =====================================================
        # ACCEPT
        # =====================================================

        if (
            validation["grounded"]
            and validation["relevant"]
            and not validation["hallucination"]
        ):

            return {
                "allowed": True,
                "grounded": True,
                "category": "grounded",
                "reason": validation["reason"],
                "answer": answer,
                "agent": "answer_guardrail"
            }

        # =====================================================
        # REJECT
        # =====================================================

        # =====================================================
        # REJECT
        # =====================================================

        return {
            "allowed": False,
            "grounded": False,
            "category": validation["category"],
            "reason": validation["reason"],
            "answer": (
                "The requested information is not present "
                "in the document."
            ),
            "agent": "answer_guardrail"
        }

    # =========================================================
    # PARSE RESPONSE
    # =========================================================

    @staticmethod
    def _parse_response(
        response: str
    ) -> dict:

        try:

            cleaned = response.strip()

            # Remove ```json
            if cleaned.startswith(
                "```json"
            ):

                cleaned = cleaned[7:]

            # Remove ```
            elif cleaned.startswith(
                "```"
            ):

                cleaned = cleaned[3:]

            if cleaned.endswith(
                "```"
            ):

                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            result = json.loads(
                cleaned
            )

            # -------------------------------------------------
            # Validate fields
            # -------------------------------------------------

            grounded = bool(
                result.get(
                    "grounded",
                    False
                )
            )

            relevant = bool(
                result.get(
                    "relevant",
                    False
                )
            )

            hallucination = bool(
                result.get(
                    "hallucination",
                    True
                )
            )

            category = result.get(
                "category",
                "unsupported_claim"
            )

            reason = result.get(
                "reason",
                "Unable to verify the answer."
            )

            return {
                "grounded": grounded,
                "relevant": relevant,
                "hallucination": hallucination,
                "category": category,
                "reason": reason
            }

        except Exception as e:

            print(
                "[ANSWER GUARDRAIL] "
                "Failed to parse response:",
                e,
                flush=True
            )

            # -------------------------------------------------
            # Fail closed
            # -------------------------------------------------

            return {
                "grounded": False,
                "relevant": False,
                "hallucination": True,
                "category": "validation_error",
                "reason": (
                    "The answer could not be reliably validated."
                )
            }