import streamlit as st

NAV_ITEMS = [
    ("Workspace", "🧩"),
    ("History", "🕘"),
    ("New Chat", "➕"),
    ("Delete Workspace", "🗑️"),
    ("Delete History", "🗑️"),
]

ICON_MAP = {
    "pdf": "📕", "docx": "📘", "txt": "📄",
    "csv": "📊", "png": "🖼️", "jpg": "🖼️",
    "jpeg": "🖼️", "md": "📝",
}


def render():
    with st.sidebar:
        st.markdown("### 🧊 GenericRAG **AI**")
        st.markdown("---")

        for label, icon in NAV_ITEMS:
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                _handle_nav(label)

        st.markdown("---")
        _render_workspace_editor()
        st.markdown("")
        _render_documents()
        st.markdown("---")
        _render_user_footer()


def _handle_nav(label: str):
    if label == "New Chat":
        st.session_state.messages = []
        st.rerun()
    elif label == "Delete Workspace":
        st.session_state.uploaded_files = []
        st.session_state.is_indexed = False
        st.session_state.messages = []
        st.rerun()
    elif label == "Delete History":
        st.session_state.messages = []
        st.rerun()
    # "Workspace" / "History" are navigation placeholders — wire these up to
    # your own view-switching logic if you add multiple pages/workspaces.


def _render_workspace_editor():
    st.caption("CURRENT WORKSPACE")
    if st.session_state.editing_workspace_name:
        new_name = st.text_input(
            "Workspace name",
            value=st.session_state.workspace_name,
            label_visibility="collapsed",
            key="workspace_name_input",
        )
        c1, c2 = st.columns(2)
        if c1.button("Save", key="save_ws_name", use_container_width=True):
            st.session_state.workspace_name = new_name.strip() or st.session_state.workspace_name
            st.session_state.editing_workspace_name = False
            st.rerun()
        if c2.button("Cancel", key="cancel_ws_name", use_container_width=True):
            st.session_state.editing_workspace_name = False
            st.rerun()
    else:
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"**{st.session_state.workspace_name}**")
        if c2.button("✏️", key="edit_ws_name"):
            st.session_state.editing_workspace_name = True
            st.rerun()


def _render_documents():
    files = st.session_state.uploaded_files
    st.caption(f"DOCUMENTS  ·  {len(files)}")
    if not files:
        st.caption("No documents uploaded.")
        return
    for f in files:
        ext = f["name"].rsplit(".", 1)[-1].lower() if "." in f["name"] else ""
        icon = ICON_MAP.get(ext, "📄")
        size_kb = (f.get("size") or 0) / 1024
        st.markdown(f"{icon} **{f['name']}**")
        st.caption(f"{size_kb:,.1f} KB")


def _render_user_footer():
    c1, c2 = st.columns([1, 4])
    c1.markdown("🙂")
    c2.markdown("**User**  \n:gray[Free Plan]")