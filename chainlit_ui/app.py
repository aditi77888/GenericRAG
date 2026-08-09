import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

import chainlit as cl

from chunkers.recursive_chunker import RecursiveChunker
from embeddings.embedding_factory import EmbeddingFactory
from llms.llm_factory import LLMFactory
from prompts.prompt_builder import PromptBuilder
from retriever.retriever_factory import RetrieverFactory
from vectorstore.vectorstore_factory import VectorStoreFactory
from pipelines.rag_pipeline import RAGPipeline

from agents.guardrail_agent import GuardrailAgent
from agents.supervisor_agent import SupervisorAgent
from agents.greeting_agent import GreetingAgent
from agents.rag_agent import RAGAgent

_RAG_PIPELINE = None

# =========================================================
# CREATE RAG PIPELINE
# =========================================================


_RAG_PIPELINE = None


def create_rag_pipeline():

    global _RAG_PIPELINE

    # =====================================================
    # REUSE EXISTING PIPELINE
    # =====================================================

    if _RAG_PIPELINE is not None:

        print(
            "[RAG INIT] Reusing existing RAG pipeline...",
            flush=True
        )

        return _RAG_PIPELINE

    # =====================================================
    # CREATE PIPELINE
    # =====================================================

    print(
        "\n[RAG INIT] Starting pipeline creation...",
        flush=True
    )

    print(
        "[RAG INIT] Creating chunker...",
        flush=True
    )

    chunker = RecursiveChunker(
        chunk_size=500,
        chunk_overlap=50
    )

    print(
        "[RAG INIT] Creating embedding model...",
        flush=True
    )

    embedding_model = EmbeddingFactory.create(
        "bge"
    )

    print(
        "[RAG INIT] Embedding model created!",
        flush=True
    )

    print(
        "[RAG INIT] Creating vector store...",
        flush=True
    )

    vector_store = VectorStoreFactory.create(
        "pinecone"
    )

    print(
        "[RAG INIT] Vector store created!",
        flush=True
    )

    print(
        "[RAG INIT] Creating retriever...",
        flush=True
    )

    retriever = RetrieverFactory.create(
        retriever_name="vector",
        embedding_model=embedding_model,
        vector_store=vector_store
    )

    print(
        "[RAG INIT] Retriever created!",
        flush=True
    )

    print(
        "[RAG INIT] Creating LLM...",
        flush=True
    )

    llm = LLMFactory.create(
        llm_name="fallback"
    )

    print(
        "[RAG INIT] LLM created!",
        flush=True
    )

    print(
        "[RAG INIT] Creating prompt builder...",
        flush=True
    )

    prompt_builder = PromptBuilder()

    print(
        "[RAG INIT] Prompt builder created!",
        flush=True
    )

    _RAG_PIPELINE = RAGPipeline(
        chunker=chunker,
        embedding_model=embedding_model,
        vector_store=vector_store,
        retriever=retriever,
        llm=llm,
        prompt_builder=prompt_builder
    )

    print(
        "[RAG INIT] COMPLETE!",
        flush=True
    )

    return _RAG_PIPELINE
# =========================================================
# CHAT START
# =========================================================



@cl.on_chat_start
async def start():

    print("\n[CHAINLIT] on_chat_start triggered", flush=True)

    guardrail = GuardrailAgent()
    supervisor = SupervisorAgent()
    greeting_agent = GreetingAgent()

    cl.user_session.set(
        "guardrail",
        guardrail
    )

    cl.user_session.set(
        "supervisor",
        supervisor
    )

    cl.user_session.set(
        "greeting_agent",
        greeting_agent
    )

    print(
        "[CHAINLIT] Agents initialized",
        flush=True
    )

    await cl.Message(
        content="## 📄 GenericRAG\n\n"
                "Upload a PDF and I will process it for you."
    ).send()

    print("[CHAINLIT] Welcome message sent", flush=True)

    files = await cl.AskFileMessage(
        content="📄 Please upload a PDF to begin.",
        accept=["application/pdf"],
        max_size_mb=20,
        max_files=1,
        timeout=300,
        raise_on_timeout=False
    ).send()

    print("[CHAINLIT] AskFileMessage completed", flush=True)

    if not files:

        await cl.Message(
            content="❌ No PDF was uploaded."
        ).send()

        return

    uploaded_file = files[0]

    print(
        f"[CHAINLIT] File received: {uploaded_file.name}",
        flush=True
    )

    await cl.Message(
        content=(
            f"📄 **{uploaded_file.name}** uploaded.\n\n"
            "⏳ Processing your document..."
        )
    ).send()

    print(
        "[CHAINLIT] Processing message sent",
        flush=True
    )

    try:

        print(
            "[CHAINLIT] Creating RAG pipeline...",
            flush=True
        )

        rag = create_rag_pipeline()

        print(
            "[CHAINLIT] RAG pipeline created!",
            flush=True
        )

        cl.user_session.set(
            "rag",
            rag
        )

        print(
            "[CHAINLIT] RAG stored in session",
            flush=True
        )

        document_id = rag.ingest(
            uploaded_file.path
        )

        print(
            f"[CHAINLIT] Document indexed: {document_id}",
            flush=True
        )

        cl.user_session.set(
            "document_id",
            document_id
        )

        cl.user_session.set(
            "filename",
            uploaded_file.name
        )

        print(
            "[CHAINLIT] Session data stored",
            flush=True
        )

        await cl.Message(
            content=(
                f"## ✅ {uploaded_file.name} is ready!\n\n"
                "Your document has been processed successfully.\n\n"
                "You can now ask questions about the PDF."
            )
        ).send()

        print(
            "[CHAINLIT] SUCCESS MESSAGE SENT",
            flush=True
        )

    except Exception as e:

        print(
            "[CHAINLIT] ERROR:",
            repr(e),
            flush=True
        )

        await cl.Message(
            content=(
                "❌ **Failed to process the PDF.**\n\n"
                f"Error: `{str(e)}`"
            )
        ).send()

# =========================================================
# MESSAGE HANDLER
# =========================================================

@cl.on_message
async def on_message(message: cl.Message):

    query = message.content.strip()

    print("\n" + "=" * 70, flush=True)
    print("[CHAINLIT] USER QUERY:", query)
    print("=" * 70, flush=True)

    # =====================================================
    # 1. GUARDRAIL
    # =====================================================
    # GET AGENTS FROM SESSION
    # =====================================================

    guardrail = cl.user_session.get("guardrail")
    supervisor = cl.user_session.get("supervisor")
    greeting_agent = cl.user_session.get("greeting_agent")

    if (
            guardrail is None
            or supervisor is None
            or greeting_agent is None
    ):
        await cl.Message(
            content=(
                "⚠️ Agent system is not initialized. "
                "Please refresh the page."
            )
        ).send()

        return



    # =====================================================
    # 1. GUARDRAIL
    # =====================================================

    print(
        "[CHAINLIT] Running GuardrailAgent...",
        flush=True
    )

    guardrail_result = guardrail.handle(
        query=query
    )
    print(
        "[CHAINLIT] GUARDRAIL:",
        guardrail_result,
        flush=True
    )

    if not guardrail_result["allowed"]:

        await cl.Message(
            content="I can't help with that request."
        ).send()

        return

    # =====================================================
    # 2. SUPERVISOR
    # =====================================================

    print(
        "[CHAINLIT] Running SupervisorAgent...",
        flush=True
    )

    route = supervisor.handle(query)

    print(
        "[CHAINLIT] SUPERVISOR:",
        route,
        flush=True
    )

    # =====================================================
    # 3. GREETING
    # =====================================================

    if route["agent"] == "greeting":

        print(
            "[CHAINLIT] Routing → GreetingAgent",
            flush=True
        )

        response = greeting_agent.handle(
            query=query,
            intent=route["intent"],
            language=route["language"]
        )

        await cl.Message(
            content=response
        ).send()

        return

    # =====================================================
    # 4. RAG REQUIRES DOCUMENT
    # =====================================================

    rag_pipeline = cl.user_session.get("rag")
    document_id = cl.user_session.get("document_id")

    if rag_pipeline is None or document_id is None:

        await cl.Message(
            content=(
                "📄 Please upload a PDF first so I can "
                "answer document-related questions."
            )
        ).send()

        return

    # =====================================================
    # 5. RAG AGENT
    # =====================================================

    if route["agent"] == "rag":

        print(
            "[CHAINLIT] Routing → RAGAgent",
            flush=True
        )

        rag_agent = RAGAgent(
            rag_pipeline=rag_pipeline
        )

        try:

            result = rag_agent.handle(
                query=query,
                document_id=document_id,
                intent=route.get(
                    "intent",
                    "document_question"
                )
            )

            print(
                "[CHAINLIT] RAG RESULT:",
                result,
                flush=True
            )

            answer = result.get(
                "answer",
                "I don't have enough information to answer this question."
            )

            sources = result.get(
                "sources",
                []
            )

            response = answer

            if sources:

                response += "\n\n### Sources\n"

                for source in sources:
                    response += f"- {source}\n"

            await cl.Message(
                content=response
            ).send()

        except Exception as e:

            print(
                "[CHAINLIT] RAG ERROR:",
                repr(e),
                flush=True
            )

            await cl.Message(
                content=(
                    "Sorry, something went wrong while "
                    "processing your question."
                )
            ).send()

        return

    # =====================================================
    # 6. UNKNOWN ROUTE
    # =====================================================

    print(
        "[CHAINLIT] ERROR: Unknown agent:",
        route.get("agent"),
        flush=True
    )

    await cl.Message(
        content="I couldn't determine how to handle that request."
    ).send()