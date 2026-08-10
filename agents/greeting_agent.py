from agents.base_agent import BaseAgent
from llms.llm_factory import LLMFactory


class GreetingAgent(BaseAgent):

    def __init__(self):

        self.llm = LLMFactory.create(
            llm_name="fallback"
        )

    def handle(
        self,
        query: str,
        intent: str,
        language: str
    ) -> str:

        query = query.strip()

        language = (
            language or "english"
        ).lower().strip()

        intent = (
            intent or "conversation"
        ).lower().strip()

        prompt = f"""
You are the conversational assistant of a PDF-based RAG application.

The user is having a conversational interaction. This request does
NOT require retrieving information from uploaded documents.

Respond naturally and appropriately to the user's message.

User message:
{query}

Detected language:
{language}

Detected intent:
{intent}

Rules:

1. Do NOT retrieve information from documents.
2. Do NOT mention Pinecone, embeddings, vector databases, RAG,
   retrieval, agents, routing, or internal implementation.
3. Do NOT make up information from any uploaded PDF.
4. Understand the user's actual message yourself. The detected intent
   is only a hint and should not override the meaning of the query.
5. Respond in the same language as the user.
6. If the user uses Hinglish, respond naturally in Hinglish.
7. Keep the response concise and conversational.
8. If the user asks what you can do or how you can help, explain that
   you can process uploaded PDF documents and answer questions about
   their contents.
9. If the user greets you, greet them naturally.
10. If the user thanks you, respond appropriately.
11. If the user says goodbye, respond appropriately.
12. Do not use a fixed or predefined response. Generate the response
    based on the user's actual message.

Return only the response to the user.
"""

        try:

            response = self.llm.generate(
                prompt
            )

            if response is None:
                return (
                    "Hello! How can I help you?"
                )

            response = str(
                response
            ).strip()

            if not response:
                return (
                    "Hello! How can I help you?"
                )

            return response

        except Exception as e:

            print(
                "[GREETING AGENT] LLM failed:",
                repr(e),
                flush=True
            )

            # Very small emergency fallback.
            # This is NOT the normal response mechanism.
            return (
                "Hello! How can I help you?"
            )