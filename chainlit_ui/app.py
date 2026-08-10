import sys
import uuid
import asyncio
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(PROJECT_ROOT))

import chainlit as cl
from memory.chat_memory import ChatMemory
import httpx

API_URL = "http://127.0.0.1:8001"

async def update_chat_history_sidebar():

    chat_memory = cl.user_session.get("chat_memory")
    documents = cl.user_session.get("documents") or []

    sidebar_content = "# 💬 Chat History\n\n"

    # =====================================================
    # UPLOADED DOCUMENTS
    # =====================================================

    sidebar_content += "## 📄 Uploaded Documents\n\n"

    if documents:

        for document in documents:

            file_name = document.get(
                "file_name",
                document.get("name", "Unknown PDF")
            )

            chunk_count = document.get(
                "chunk_count",
                "?"
            )

            sidebar_content += (
                f"📄 **{file_name}**  \n"
                f"_{chunk_count} chunks indexed_\n\n"
            )

    else:

        sidebar_content += (
            "_No documents uploaded yet._\n\n"
        )

    sidebar_content += "---\n\n"

    # =====================================================
    # CHAT HISTORY
    # =====================================================

    sidebar_content += "## 💬 Conversations\n\n"

    if chat_memory is None or not chat_memory.turns:

        sidebar_content += "_No conversation yet._\n"

    else:

        for i, turn in enumerate(
            chat_memory.turns,
            start=1
        ):

            sidebar_content += (
                f"### {i}. User\n"
                f"{turn['question']}\n\n"
                f"**Assistant:**\n"
                f"{turn['answer']}\n\n"
                "---\n\n"
            )

    # =====================================================
    # UPDATE SIDEBAR
    # =====================================================

    await cl.ElementSidebar.set_title(
        "Chat History"
    )

    await cl.ElementSidebar.set_elements(
        [
            cl.Text(
                name="chat_history",
                content=sidebar_content
            )
        ]
    )

@cl.on_chat_start
async def start():

    print(
        "\n[CHAINLIT] on_chat_start triggered",
        flush=True
    )
    # =====================================================
    # CREATE CHAT MEMORY
    # =====================================================
    chat_memory = ChatMemory(
        max_turns=6
    )

    cl.user_session.set(
        "chat_memory",
        chat_memory
    )

    # =====================================================
    # CREATE SESSION NAMESPACE
    # =====================================================

    namespace = f"session_{uuid.uuid4().hex}"

    cl.user_session.set(
        "namespace",
        namespace
    )

    # =====================================================
    # DOCUMENT LIST
    # =====================================================

    cl.user_session.set(
        "documents",
        []
    )

    # =====================================================
    # SIDEBAR
    # =====================================================

    await update_chat_history_sidebar()

    print(
        "[CHAINLIT] Session initialized",
        flush=True
    )

@cl.on_message
async def on_message(message: cl.Message):

    query = (
        message.content or ""
    ).strip()

    print(
        "\n" + "=" * 70,
        flush=True
    )

    print(
        "[CHAINLIT] USER QUERY:",
        query,
        flush=True
    )

    print(
        "=" * 70,
        flush=True
    )

    # =====================================================
    # SESSION DATA
    # =====================================================

    namespace = cl.user_session.get(
        "namespace"
    )

    chat_memory = cl.user_session.get(
        "chat_memory"
    )

    documents = (
        cl.user_session.get(
            "documents"
        )
        or []
    )

    # =====================================================
    # HANDLE PDF UPLOAD
    # =====================================================

    message_elements = (
            message.elements
            or []
    )

    print(
        f"[CHAINLIT] Message elements: {len(message_elements)}",
        flush=True
    )

    pdf_elements = []

    for element in message_elements:

        file_name = (
                getattr(
                    element,
                    "name",
                    ""
                )
                or ""
        )

        mime_type = (
                getattr(
                    element,
                    "mime",
                    ""
                )
                or ""
        )

        file_path = getattr(
            element,
            "path",
            None
        )

        print(
            "[CHAINLIT] Element:",
            {
                "name": file_name,
                "mime": mime_type,
                "path": file_path
            },
            flush=True
        )

        if file_name.lower().endswith(".pdf"):
            pdf_elements.append(
                element
            )
    # =====================================================
    # PROCESS PDFs
    # =====================================================

    if pdf_elements:

        for element in pdf_elements:

            file_name = getattr(
                element,
                "name",
                "document.pdf"
            )

            status_msg = cl.Message(
                content=(
                    f"📄 **{file_name}** — processing..."
                )
            )

            await status_msg.send()

            try:

                result = await upload_pdf_to_server(
                    element,
                    namespace
                )

                if not result.get(
                    "success",
                    False
                ):

                    raise Exception(
                        result.get(
                            "error",
                            "Unknown ingestion error"
                        )
                    )

                document = result.get(
                    "document"
                )

                if document:

                    documents.append(
                        document
                    )

                cl.user_session.set(
                    "documents",
                    documents
                )

                status_msg.content = (
                    f"📄 **{file_name}**\n"
                    f"✓ Document uploaded"
                )

                await status_msg.update()

                print(
                    f"[CHAINLIT] Uploaded: {file_name}",
                    flush=True
                )

            except Exception as e:

                print(
                    "[CHAINLIT] UPLOAD ERROR:",
                    repr(e),
                    flush=True
                )

                status_msg.content = (
                    f"❌ **{file_name}** failed to upload."
                )

                await status_msg.update()

        await update_chat_history_sidebar()

        # -------------------------------------------------
        # If only PDF was attached, stop.
        # -------------------------------------------------

        if not query:

            return

    # =====================================================
    # NO QUERY
    # =====================================================

    if not query:

        return

    # =====================================================
    # CHECK DOCUMENT
    # =====================================================

    # We only need this check for RAG questions.
    # The server itself decides whether the query
    # is greeting or RAG.

    # =====================================================
    # PREPARE CHAT HISTORY
    # =====================================================

    chat_history = (
        chat_memory.get_history_text()
        if chat_memory is not None
        else None
    )

    # =====================================================
    # SEND QUERY TO FASTAPI
    # =====================================================

    try:

        result = await ask_rag_server(
            question=query,
            namespace=namespace,
            chat_history=chat_history
        )

        print(
            "[CHAINLIT] SERVER RESPONSE:",
            result,
            flush=True
        )

        answer = result.get(
            "answer",
            "I couldn't generate a response."
        )

        sources = result.get(
            "sources",
            []
        )

        response = answer

        # =================================================
        # SOURCES
        # =================================================

        if sources:

            response += (
                "\n\n### Sources\n"
            )

            for source in sources:

                response += (
                    f"- {source}\n"
                )

        # =================================================
        # SEND RESPONSE
        # =================================================

        await cl.Message(
            content=response
        ).send()

        # =================================================
        # MEMORY
        # =================================================

        if chat_memory is not None:

            chat_memory.add_turn(
                query,
                answer
            )

            await update_chat_history_sidebar()

    except Exception as e:

        print(
            "[CHAINLIT] SERVER ERROR:",
            repr(e),
            flush=True
        )

        await cl.Message(
            content=(
                "Sorry, something went wrong while "
                "processing your request."
            )
        ).send()


async def upload_pdf_to_server(
    element,
    namespace
):

    file_name = (
        getattr(
            element,
            "name",
            "document.pdf"
        )
        or "document.pdf"
    )

    file_path = getattr(
        element,
        "path",
        None
    )

    print(
        f"[CHAINLIT] File detected: {file_name}",
        flush=True
    )

    print(
        f"[CHAINLIT] File path: {file_path}",
        flush=True
    )

    if not file_path:

        raise ValueError(
            f"Uploaded file path is unavailable for {file_name}."
        )

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            f"Uploaded file does not exist: {file_path}"
        )

    file_size = os.path.getsize(
        file_path
    )

    print(
        f"[CHAINLIT] File size: {file_size} bytes",
        flush=True
    )

    if file_size == 0:

        raise ValueError(
            f"Uploaded file is empty: {file_name}"
        )

    print(
        f"[CHAINLIT] Sending {file_name} to FastAPI...",
        flush=True
    )

    timeout = httpx.Timeout(
        connect=30.0,
        read=600.0,
        write=600.0,
        pool=30.0
    )

    with open(
        file_path,
        "rb"
    ) as f:

        files = {
            "file": (
                file_name,
                f,
                "application/pdf"
            )
        }

        data = {
            "namespace": namespace
        }

        async with httpx.AsyncClient(
            timeout=timeout
        ) as client:

            response = await client.post(
                f"{API_URL}/ingest",
                files=files,
                data=data
            )

    print(
        f"[CHAINLIT] FastAPI status: {response.status_code}",
        flush=True
    )

    print(
        f"[CHAINLIT] FastAPI response: {response.text}",
        flush=True
    )

    response.raise_for_status()

    result = response.json()

    if not result.get(
        "success",
        False
    ):

        raise RuntimeError(
            result.get(
                "error",
                "FastAPI ingestion failed."
            )
        )

    return result

async def ask_rag_server(
    question,
    namespace,
    chat_history
):

    payload = {
        "question": question,
        "namespace": namespace,
        "chat_history": chat_history
    }

    print(
        "[CHAINLIT] Sending query to FastAPI...",
        flush=True
    )

    timeout = httpx.Timeout(
        connect=30.0,
        read=600.0,
        write=600.0,
        pool=30.0
    )

    async with httpx.AsyncClient(
            timeout=timeout
    ) as client:
        response = await client.post(
            f"{API_URL}/query",
            json=payload
        )
    print(
        f"[CHAINLIT] Query status: {response.status_code}",
        flush=True
    )

    response.raise_for_status()

    return response.json()