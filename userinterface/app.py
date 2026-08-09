
import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import os

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
#from loaders.loader_factory import LoaderFactory

st.set_page_config(
    page_title="GenericRAG AI",
    page_icon="🤖",
    layout="wide"
)

st.markdown(
    load_css(),
    unsafe_allow_html=True
)

initialize()



if st.session_state.pipeline is None:

    chunker = RecursiveChunker()

    embedding_model = EmbeddingFactory.create("qwen")

    vector_store = VectorStoreFactory.create("pinecone")

    retriever = VectorRetriever(
        embedding_model,
        vector_store
    )

    llm = LLMFactory.create("gemini")

    prompt_builder = PromptBuilder()

    # Dummy loader (will be replaced automatically)
    #loader = LoaderFactory.create("sample.pdf")

    st.session_state.pipeline = RAGPipeline(
        chunker,
        embedding_model,
        vector_store,
        retriever,
        llm,
        prompt_builder
    )

render_sidebar()

render_chat()

st.write("")

question = st.chat_input(
    "Ask about your documents..."
)

col1, col2, col3, col4 = st.columns(
    [2,2,2,1]
)

with col1:

    uploaded_files = st.file_uploader(

        "📎 Upload Documents",

        type=[
            "pdf",
            "docx",
            "txt",
            "csv",
            "png",
            "jpg",
            "jpeg",
            "md"
        ],

        accept_multiple_files=True,

        label_visibility="collapsed"
    )

with col2:

    st.session_state.llm = st.selectbox(

        "LLM",

        [

            "Gemini",

            "Groq"

        ],

        label_visibility="collapsed"
    )

with col3:

    st.session_state.web_search = st.toggle(

        "🌐 Web Search",

        value=False
    )

with col4:

    st.button(
        "🎤"
    )


UPLOAD_DIR = os.path.join(
    os.getcwd(),
    "uploads"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)

if uploaded_files and not st.session_state.is_indexed:

    saved_paths = []

    st.session_state.uploaded_files = []

    for file in uploaded_files:

        save_path = os.path.join(
            UPLOAD_DIR,
            file.name
        )

        with open(
                save_path,
                "wb"
        ) as f:

            f.write(
                file.getbuffer()
            )

        saved_paths.append(save_path)

        st.session_state.uploaded_files.append(
            file.name
        )

    with st.spinner("Indexing documents..."):

        total_chunks = st.session_state.pipeline.index_documents(
            saved_paths,
            namespace="workspace"
        )

    st.success(
        f"{len(saved_paths)} files indexed ({total_chunks} chunks)"
    )

    st.session_state.is_indexed = True


if question:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":question
        }
    )

    with st.spinner("Thinking..."):
        result = st.session_state.pipeline.ask(
            question,
            namespace="workspace"
        )

    st.session_state.messages.append(

        {

            "role": "assistant",

            "content": result["answer"],

            "sources": result["sources"],

            "chunks": result["chunks"],

            "benchmarks": {}

        }

    )

    st.session_state.messages.append(

        {

            "role":"assistant",

            "content":answer,

            "sources":[],

            "chunks":[],

            "benchmarks":{}

        }

    )




    st.rerun()

