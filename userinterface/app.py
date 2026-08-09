import streamlit as st

from ui.styles import load_css
from ui.sidebar import render as render_sidebar
from ui.chat import render as render_chat
from ui.session import initialize
from ui.uploader import render as render_uploader

st.set_page_config(

    page_title="GenericRAG",

    layout="wide"
)

st.markdown(
    load_css(),
    unsafe_allow_html=True
)

initialize()

render_sidebar()

render_chat()

uploaded_files = render_uploader()

question = st.chat_input(
    "Ask!"
)

if question:

    st.session_state.messages.append(
        {
            "role":"user",
            "content":question
        }
    )

    st.rerun()