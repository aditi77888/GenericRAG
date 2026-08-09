import streamlit as st


def render():

    with st.sidebar:

        st.title("📂 Workspace")

        st.button("➕ New Chat")

        st.button("🗑 Delete Workspace")

        st.button("🗑 Delete History")

        st.divider()

        st.subheader("History")

        for i in range(5):
            st.button(f"Conversation {i+1}")