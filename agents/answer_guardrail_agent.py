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

        context_parts = []

        for i, chunk in enumerate(chunks):

            text = chunk.content

            context_parts.append(
                f"""
--- CONTEXT CHUNK {i + 1} ---

{text}
"""
            )

        context = "\n".join(
            context_parts
        )

        # =====================================================
        # VALIDATION PROMPT
        # =====================================================

        prompt = f"""
You are an Answer Validation Guardrail for a RAG system.

Your job is to determine whether the generated answer is
supported by the retrieved document context.

You MUST NOT answer the user's question.

You ONLY validate the generated answer.

USER QUESTION:
{question}

RETRIEVED DOCUMENT CONTEXT:
{context}

GENERATED ANSWER:
{answer}

Evaluate the generated answer using these rules:

1. GROUNDED
   The answer must be directly supported by the retrieved
   document context.

2. NO HALLUCINATION
   The answer must not introduce facts, names, numbers,
   dates, claims, or explanations that are not supported
   by the retrieved context.

3. QUESTION RELEVANCE
   The answer must actually answer the user's question.

4. NO OUTSIDE KNOWLEDGE
   Do not allow information that comes from general knowledge
   rather than the retrieved document.

5. PARTIAL ANSWERS
   If only part of the answer is supported by the context,
   mark it as not grounded.

Return ONLY valid JSON.

Required format:

{{
    "grounded": true or false,
    "relevant": true or false,
    "hallucination": true or false,
    "category": "grounded" or "unsupported_claim" or "hallucination" or "irrelevant",
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

        return {
            "allowed": False,
            "grounded": False,
            "category": validation["category"],
            "reason": validation["reason"],
            "answer": (
                "I couldn't verify that answer against "
                "the information available in the document."
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