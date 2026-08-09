import streamlit as st
from session import (
    clear_chat,
    clear_workspace,
    clear_history
)


def render():

    with st.sidebar:

        st.title("📂 Workspace")

        st.markdown("---")

        # ==========================
        # Uploaded Documents
        # ==========================

        st.subheader("📄 Uploaded Documents")

        if st.session_state.uploaded_files:

            for file in st.session_state.uploaded_files:

                st.markdown(f"📄 {file}")

        else:

            st.caption("No documents uploaded.")

        st.markdown("---")

        # ==========================
        # Workspace Buttons
        # ==========================

        if st.button(
                "➕ New Chat",
                use_container_width=True
        ):
            clear_chat()

        if st.button(
                "🗑 Delete Workspace",
                use_container_width=True
        ):
            clear_workspace()

        if st.button(
                "🗑 Delete History",
                use_container_width=True
        ):
            clear_history()

        st.markdown("---")

        # ==========================
        # Chat History
        # ==========================

        st.subheader("💬 History")

        if st.session_state.chat_history:

            for chat in st.session_state.chat_history:

                st.button(
                    chat,
                    use_container_width=True
                )

        else:

            st.caption("No previous chats.")