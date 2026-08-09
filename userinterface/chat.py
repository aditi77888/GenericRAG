import streamlit as st


def render():

    st.markdown(
        "<h1 class='title'>GenericRAG AI</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='subtitle'>How can I help you today?</p>",
        unsafe_allow_html=True
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.write(message["content"])