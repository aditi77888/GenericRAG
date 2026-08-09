import streamlit as st


def initialize():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "workspace" not in st.session_state:
        st.session_state.workspace = []

    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None