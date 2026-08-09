import streamlit as st

def render():
    messages = st.session_state.messages

    if not messages:
        _render_empty_state()
        return

    for i, msg in enumerate(messages):
        role = msg.get("role", "assistant")
        avatar = "🧑" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.write(msg.get("content", ""))
            if msg.get("timestamp"):
                st.caption(msg["timestamp"])

        # Only show the retrieved-context/benchmarks/model-info row under the
        # most recent assistant answer, matching the mockup.
        if role == "assistant" and i == len(messages) - 1:
            _render_info_cards(msg)


def _render_empty_state():
    st.markdown(
        """
        <div style="text-align:center; padding-top:2rem;">
            <div style="font-size:3rem;">🤖</div>
            <h1>GenericRAG <span style="color:#6C5CE7;">AI</span></h1>
            <p style="color:#6B7280;">How can I help you today?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_info_cards(msg: dict):
    sources = msg.get("sources") or []
    benchmarks = msg.get("benchmarks") or {}

    if not (sources or benchmarks):
        return  # nothing to show yet (e.g. benchmarks not computed)

    if not st.session_state.get("show_benchmarks_panel", True):
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("**📄 Retrieved Context**")
            if sources:
                for s in sources[:5]:
                    name = s.get("file") or s.get("source") or "Document"
                    page = s.get("page")
                    score = s.get("score")
                    snippet = (s.get("text") or s.get("snippet") or "")[:140]
                    header = name + (f" · Page {page}" if page else "")
                    st.markdown(f"**{header}**")
                    if isinstance(score, (int, float)):
                        st.caption(f"Score: {score:.2f}")
                    if snippet:
                        st.caption(snippet)
                    st.divider()
            else:
                st.caption("No retrieved chunks available.")

    with col2:
        with st.container(border=True):
            st.markdown("**📊 Benchmarks**")
            if benchmarks:
                for k, v in benchmarks.items():
                    try:
                        val = float(v)
                    except (TypeError, ValueError):
                        continue
                    st.caption(k)
                    st.progress(min(max(val, 0.0), 1.0), text=f"{val:.2f}")
            else:
                st.caption("Benchmarks not computed for this answer.")

    with col3:
        with st.container(border=True):
            st.markdown("**ℹ️ Model Info**")
            model_info = msg.get("model_info") or {}
            info = {
                "Model": model_info.get("model", st.session_state.llm),
                "Web Search": "On" if st.session_state.web_search else "Off",
            }
            info.update(model_info.get("extra", {}))
            for k, v in info.items():
                st.markdown(f"**{k}:** {v}")