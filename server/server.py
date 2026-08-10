import sys
import uuid
import tempfile
import os
from pathlib import Path
import asyncio
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# PROJECT IMPORTS
# =========================================================

from embeddings.embedding_singleton import get_embedding_model
from chunkers.recursive_chunker import RecursiveChunker
from llms.llm_factory import LLMFactory
from prompts.prompt_builder import PromptBuilder
from retriever.retriever_factory import RetrieverFactory
from vectorstore.vectorstore_factory import VectorStoreFactory
from pipelines.rag_pipeline import RAGPipeline

from agents.guardrail_agent import GuardrailAgent
from agents.supervisor_agent import SupervisorAgent
from agents.greeting_agent import GreetingAgent
from agents.rag_agent import RAGAgent


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="GenericRAG API",
    description="Backend API for GenericRAG",
    version="1.0.0"
)


# =========================================================
# GLOBAL RAG PIPELINE
# =========================================================

_RAG_PIPELINE = None


def create_rag_pipeline():

    global _RAG_PIPELINE

    if _RAG_PIPELINE is not None:

        print(
            "[SERVER] Reusing existing RAG pipeline",
            flush=True
        )

        return _RAG_PIPELINE

    print(
        "[SERVER] Creating RAG pipeline...",
        flush=True
    )

    chunker = RecursiveChunker(
        chunk_size=500,
        chunk_overlap=50
    )

    embedding_model = get_embedding_model("bge")

    vector_store = VectorStoreFactory.create(
        "pinecone"
    )

    retriever = RetrieverFactory.create(
        retriever_name="vector",
        embedding_model=embedding_model,
        vector_store=vector_store
    )

    llm = LLMFactory.create(
        llm_name="fallback"
    )

    prompt_builder = PromptBuilder()

    _RAG_PIPELINE = RAGPipeline(
        chunker=chunker,
        embedding_model=embedding_model,
        vector_store=vector_store,
        retriever=retriever,
        llm=llm,
        prompt_builder=prompt_builder
    )

    print(
        "[SERVER] RAG pipeline ready!",
        flush=True
    )

    return _RAG_PIPELINE


# =========================================================
# GLOBAL AGENTS
# =========================================================

guardrail_agent = GuardrailAgent()
supervisor_agent = SupervisorAgent()
greeting_agent = GreetingAgent()

print(
    "[SERVER] Agents initialized",
    flush=True
)


# =========================================================
# REQUEST MODELS
# =========================================================

class QueryRequest(BaseModel):

    question: str
    namespace: str
    chat_history: str | None = None


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# CREATE SESSION
# =========================================================

@app.post("/session")
def create_session():

    namespace = f"session_{uuid.uuid4().hex}"

    return {
        "namespace": namespace
    }


# =========================================================
# INGEST PDF
# =========================================================

@app.post("/ingest")
async def ingest_pdf(
    file: UploadFile = File(...),
    namespace: str = Form(...)
):

    print(
        f"[SERVER] Ingest request received: {file.filename}",
        flush=True
    )

    temp_path = None

    try:

        # -------------------------------------------------
        # Validate file
        # -------------------------------------------------

        if not file.filename:
            raise ValueError(
                "No filename was provided."
            )

        if not file.filename.lower().endswith(".pdf"):
            raise ValueError(
                "Only PDF files are supported."
            )

        if not namespace:
            raise ValueError(
                "Namespace is required."
            )

        print(
            f"[SERVER] Namespace: {namespace}",
            flush=True
        )

        # -------------------------------------------------
        # Create RAG pipeline
        # -------------------------------------------------

        rag = create_rag_pipeline()

        # -------------------------------------------------
        # Save uploaded PDF temporarily
        # -------------------------------------------------

        suffix = Path(
            file.filename
        ).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            content = await file.read()

            if not content:
                raise ValueError(
                    "Uploaded PDF is empty."
                )

            temp_file.write(content)

            temp_path = temp_file.name

        print(
            f"[SERVER] Temporary file created: {temp_path}",
            flush=True
        )

        print(
            f"[SERVER] PDF size: {len(content)} bytes",
            flush=True
        )

        # -------------------------------------------------
        # RAG INGESTION
        # -------------------------------------------------

        print(
            "[SERVER] Starting RAG ingestion...",
            flush=True
        )

        result = await asyncio.to_thread(
            rag.ingest,
            source=temp_path,
            namespace=namespace,
            file_name=file.filename
        )

        print(
            "[SERVER] RAG ingestion completed.",
            flush=True
        )

        print(
            "[SERVER] Ingestion result:",
            result,
            flush=True
        )

        return {
            "success": True,
            "file_name": file.filename,
            "document": result
        }

    except Exception as e:

        print(
            "[SERVER] INGEST ERROR:",
            repr(e),
            flush=True
        )

        return {
            "success": False,
            "file_name": file.filename,
            "error": str(e)
        }

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            try:

                os.remove(
                    temp_path
                )

                print(
                    "[SERVER] Temporary file deleted.",
                    flush=True
                )

            except Exception as e:

                print(
                    "[SERVER] Could not delete temporary file:",
                    repr(e),
                    flush=True
                )
# =========================================================
# QUERY
# =========================================================

@app.post("/query")
def query(request: QueryRequest):

    question = request.question.strip()

    print(
        "\n" + "=" * 70,
        flush=True
    )

    print(
        "[SERVER] USER QUERY:",
        question,
        flush=True
    )

    print(
        "=" * 70,
        flush=True
    )

    # =====================================================
    # 1. GUARDRAIL
    # =====================================================

    guardrail_result = guardrail_agent.handle(
        query=question
    )

    print(
        "[SERVER] GUARDRAIL:",
        guardrail_result,
        flush=True
    )

    if not guardrail_result["allowed"]:

        return {
            "success": True,
            "type": "blocked",
            "answer": "I can't help with that request.",
            "sources": []
        }

    # =====================================================
    # 2. SUPERVISOR
    # =====================================================

    route = supervisor_agent.handle(
        question
    )

    print(
        "[SERVER] SUPERVISOR:",
        route,
        flush=True
    )

    # =====================================================
    # 3. GREETING / SMALL TALK
    # =====================================================

    if route["agent"] == "greeting":

        print(
            "[SERVER] Routing → GreetingAgent",
            flush=True
        )

        response = greeting_agent.handle(
            query=question,
            intent=route["intent"],
            language=route["language"]
        )

        return {
            "success": True,
            "type": "greeting",
            "answer": response,
            "sources": []
        }


    # =====================================================
    # 4. RAG
    # =====================================================

    if route["agent"] == "rag":

        print(
            "[SERVER] Routing → RAGAgent",
            flush=True
        )

        rag_pipeline = create_rag_pipeline()

        rag_agent = RAGAgent(
            rag_pipeline=rag_pipeline
        )

        result = rag_agent.handle(
            query=question,
            namespace=request.namespace,
            chat_history=request.chat_history,
            intent=route.get(
                "intent",
                "document_question"
            )
        )

        print(
            "[SERVER] RAG RESULT:",
            result,
            flush=True
        )

        return {
            "success": True,
            "type": "rag",
            "answer": result.get(
                "answer",
                "I don't have enough information to answer this question."
            ),
            "sources": result.get(
                "sources",
                []
            )
        }
    # =====================================================
    # 3.5 BLOCKED / OUT OF SCOPE
    # =====================================================

    if route["agent"] == "blocked":
        print(
            "[SERVER] Routing → BLOCKED",
            flush=True
        )

        return {
            "success": True,
            "type": "blocked",
            "answer": (
                "I can only answer questions related to "
                "the information available in the uploaded document."
            ),
            "sources": []
        }

    # =====================================================
    # 5. UNKNOWN ROUTE
    # =====================================================

    return {
        "success": False,
        "type": "unknown",
        "answer": "I couldn't determine how to handle that request.",
        "sources": []
    }