import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from styles import load_css
from sidebar import render as render_sidebar
from chat import render as render_chat
from session import initialize
from chunkers.recursive_chunker import RecursiveChunker
from embeddings.embedding_factory import EmbeddingFactory
from llms.llm_factory import LLMFactory
from pipelines.rag_pipeline import RAGPipeline
from prompts.prompt_builder import PromptBuilder
from retriever.vector_retriever import VectorRetriever
from vectorstore.vectorstore_factory import VectorStoreFactory
# from loaders.loader_factory import LoaderFactory

st.set_page_config(
    page_title="GenericRAG AI",
    page_icon="🤖",
    layout="wide",
)

# initialize() must run before load_css() since dark_mode lives in session_state
initialize()

st.markdown(load_css(st.session_state.dark_mode), unsafe_allow_html=True)

if st.session_state.pipeline is None:
    chunker = RecursiveChunker()
    embedding_model = EmbeddingFactory.create("qwen")
    vector_store = VectorStoreFactory.create("pinecone")
    retriever = VectorRetriever(embedding_model, vector_store)
    llm = LLMFactory.create("gemini")
    prompt_builder = PromptBuilder()

    # Dummy loader (will be replaced automatically)
    # loader = LoaderFactory.create("sample.pdf")

    st.session_state.pipeline = RAGPipeline(
        chunker,
        embedding_model,
        vector_store,
        retriever,
        llm,
        prompt_builder,
    )

render_sidebar()

# ---- Top bar --------------------------------------------------------------
top_l, top_r1, top_r2 = st.columns([8, 1.3, 1])
with top_r1:
    with st.container(key="top_benchmarks"):
        if st.button("📊 Benchmarks", use_container_width=True):
            st.session_state.show_benchmarks_panel = not st.session_state.show_benchmarks_panel
with top_r2:
    with st.container(key="top_theme"):
        icon = "☀️" if st.session_state.dark_mode else "🌙"
        if st.button(icon, use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

# ---- Chat history + empty state -------------------------------------------
render_chat()

# ---- Document chips ---------------------------------------------------------
if st.session_state.uploaded_files:
    with st.container(key="chip_row"):
        chip_cols = st.columns(len(st.session_state.uploaded_files))
        for idx, f in enumerate(st.session_state.uploaded_files):
            with chip_cols[idx]:
                if st.button(f"{f['name']}  ✕", key=f"chip_{f['name']}"):
                    st.session_state.uploaded_files = [
                        x for x in st.session_state.uploaded_files if x["name"] != f["name"]
                    ]
                    st.session_state.is_indexed = False
                    st.rerun()

# Clear the question box *before* creating the widget, if flagged from the
# previous run (Streamlit won't let you mutate a widget's value afterwards).
if st.session_state._clear_question:
    st.session_state["ask_input"] = ""
    st.session_state._clear_question = False

# ---- Input row: text box + upload (popover) + mic --------------------------
input_col, plus_col, mic_col = st.columns([10, 1, 1])
with input_col:
    with st.container(key="ask_input_wrap"):
        question = st.text_input(
            "Ask!",
            key="ask_input",
            placeholder="Ask about your documents...",
            label_visibility="collapsed",
        )
with plus_col:
    with st.popover("➕"):
        new_files = st.file_uploader(
            "📎 Upload Documents",
            type=["pdf", "docx", "txt", "csv", "png", "jpg", "jpeg", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="uploader",
        )
with mic_col:
    st.button("🎤", help="Voice input — not wired up yet")

# ---- Controls row: model select / Send / Web Search -------------------------
model_col, send_col, web_col = st.columns([2, 3, 2])
with model_col:
    st.session_state.llm = st.selectbox(
        "LLM",
        ["Gemini", "Groq"],
        index=["Gemini", "Groq"].index(st.session_state.llm),
        label_visibility="collapsed",
    )
with send_col:
    with st.container(key="send_btn"):
        send_clicked = st.button("Send", use_container_width=True)
with web_col:
    st.session_state.web_search = st.toggle(
        "🌐 Web Search",
        value=st.session_state.web_search,
    )

# ---- Handle uploads ----------------------------------------------------------
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

if new_files and not st.session_state.is_indexed:
    saved_paths = []
    st.session_state.uploaded_files = []

    for file in new_files:
        save_path = os.path.join(UPLOAD_DIR, file.name)
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        saved_paths.append(save_path)
        st.session_state.uploaded_files.append(
            {"name": file.name, "size": file.size, "path": save_path}
        )

    with st.spinner("Indexing documents..."):
        total_chunks = st.session_state.pipeline.index_documents(
            saved_paths,
            namespace="workspace",
        )

    st.success(f"{len(saved_paths)} files indexed ({total_chunks} chunks)")
    st.session_state.is_indexed = True
    st.rerun()

# ---- Handle question ----------------------------------------------------------
if send_clicked and question.strip():
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
            "timestamp": datetime.now().strftime("%I:%M %p"),
        }
    )

    with st.spinner("Thinking..."):
        result = st.session_state.pipeline.ask(question, namespace="workspace")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result.get("sources", []),
            "chunks": result.get("chunks", []),
            "benchmarks": result.get("benchmarks", {}),
            "timestamp": datetime.now().strftime("%I:%M %p"),
        }
    )

    st.session_state._clear_question = True
    st.rerun()