import streamlit as st


def render():

    # ==========================
    # Logo
    # ==========================

    st.markdown(
        """
        <div class="logo">
            🤖
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================
    # Title
    # ==========================

    st.markdown(
        """
        <div class="title">
            GenericRAG AI
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================
    # Subtitle
    # ==========================

    st.markdown(
        """
        <div class="subtitle">
            Universal Document Intelligence
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<center><h4>How can I help you today?</h4></center>",
        unsafe_allow_html=True
    )

    st.write("")

    # ==========================
    # Chat Messages
    # ==========================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            # Assistant extras
            if message["role"] == "assistant":

                # -------------------------
                # Sources
                # -------------------------

                with st.expander("📚 Sources"):

                    sources = message.get("sources", [])

                    if sources:

                        for source in sources:

                            st.write(source)

                    else:

                        st.caption("No sources available.")

                # -------------------------
                # Retrieved Chunks
                # -------------------------

                with st.expander("📄 Retrieved Context"):

                    chunks = message.get("chunks", [])

                    if chunks:

                        for i, chunk in enumerate(chunks, start=1):

                            st.markdown(f"### Chunk {i}")

                            st.write(chunk.content)

                            score = chunk.metadata.get(
                                "score",
                                "-"
                            )

                            st.caption(
                                f"Similarity Score : {score}"
                            )

                            st.divider()

                    else:

                        st.caption(
                            "No retrieved context."
                        )

                # -------------------------
                # Benchmarks
                # -------------------------

                with st.expander("📊 Benchmarks"):

                    benchmarks = message.get(
                        "benchmarks",
                        {}
                    )

                    st.write(
                        f"**Context Precision:** {benchmarks.get('context_precision','--')}"
                    )

                    st.write(
                        f"**Faithfulness:** {benchmarks.get('faithfulness','--')}"
                    )

                    st.write(
                        f"**Answer Relevancy:** {benchmarks.get('answer_relevancy','--')}"
                    )

                # -------------------------
                # Model Information
                # -------------------------

                with st.expander("⚙ Model Information"):

                    st.write(
                        f"LLM : {st.session_state.llm}"
                    )

                    st.write(
                        f"Embedding : {st.session_state.embedding_model}"
                    )

                    st.write(
                        "Vector Store : Pinecone"
                    )

                    st.write(
                        f"Web Search : {'ON' if st.session_state.web_search else 'OFF'}"
                    )