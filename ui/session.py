import streamlit as st

DEFAULTS = {
    "pipeline": None,
    "messages": [],              # list of {role, content, timestamp, sources?, chunks?, benchmarks?}
    "uploaded_files": [],        # list of {"name":..., "size":..., "path":...}
    "is_indexed": False,
    "llm": "Gemini",
    "web_search": False,
    "workspace_name": "My Workspace",
    "dark_mode": False,
    "show_benchmarks_panel": True,
    "editing_workspace_name": False,
    "_clear_question": False,
}


def initialize():
    """Populate st.session_state with default keys the app relies on."""
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            # lists/dicts must be copied per-session, not shared as one object
            st.session_state[key] = value.copy() if isinstance(value, (list, dict)) else value