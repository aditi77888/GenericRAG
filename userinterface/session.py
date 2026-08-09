import streamlit as st


def initialize():

    defaults = {

        "messages": [],

        "uploaded_files": [],

        "workspace_name": "Workspace",

        "chat_history": [],

        "pipeline": None,

        "is_indexed": False,

        "llm": "Gemini",

        "embedding_model": "Qwen3-Embedding-0.6B",

        "web_search": False,

        "benchmarks": {

            "context_precision": None,

            "faithfulness": None,

            "answer_relevancy": None

        }

    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


def clear_chat():

    st.session_state.messages = []


def clear_workspace():

    st.session_state.uploaded_files = []

    st.session_state.is_indexed = False


def clear_history():

    st.session_state.chat_history = []