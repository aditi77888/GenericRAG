from agents.base_agent import BaseAgent
from agents.answer_guardrail_agent import AnswerGuardrailAgent


class RAGAgent(BaseAgent):

    def __init__(
        self,
        rag_pipeline
    ):

        self.rag = rag_pipeline

        self.answer_guardrail = (
            AnswerGuardrailAgent()
        )

    # =========================================================
    # HANDLE
    # =========================================================

    def handle(
        self,
        query: str,
        document_id: str,
        intent: str = "document_question"
    ):

        print(
            "[RAG AGENT] Query:",
            query,
            flush=True
        )

        print(
            "[RAG AGENT] Intent:",
            intent,
            flush=True
        )

        print(
            "[RAG AGENT] Document ID:",
            document_id,
            flush=True
        )

        # =====================================================
        # RAG PIPELINE
        # =====================================================

        result = self.rag.ask(
            question=query,
            document_id=document_id
        )

        # =====================================================
        # NO CONTEXT
        # =====================================================

        if not result["chunks"]:

            print(
                "[RAG AGENT] No relevant context found.",
                flush=True
            )

            return {
                "answer": result["answer"],
                "sources": result["sources"],
                "chunks": [],
                "agent": "rag",
                "guardrail": {
                    "allowed": False,
                    "category": "no_context"
                }
            }

        # =====================================================
        # ANSWER GUARDRAIL
        # =====================================================

        print(
            "[RAG AGENT] Validating generated answer...",
            flush=True
        )

        validation = self.answer_guardrail.handle(

            question=query,

            answer=result["answer"],

            chunks=result["chunks"]
        )

        print(
            "[RAG AGENT] Answer validation:",
            validation,
            flush=True
        )

        # =====================================================
        # RETURN
        # =====================================================

        return {

            "answer": validation["answer"],

            "sources": (
                result["sources"]
                if validation["allowed"]
                else []
            ),

            "chunks": result["chunks"],

            "agent": "rag",

            "guardrail": validation
        }