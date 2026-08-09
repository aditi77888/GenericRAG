def load_css(dark_mode: bool = False) -> str:
    """Return a <style> block themeing the app to match the target mockup.

    Uses Streamlit's data-testid selectors (stable across versions) plus the
    `st.container(key=...)` -> `.st-key-<key>` hook (Streamlit >= 1.36) to
    scope styling to specific buttons/containers without fragile nth-child
    guessing.
    """

    if dark_mode:
        bg = "#12121C"
        panel = "#181826"
        card = "#1E1E2E"
        border = "#2A2A3D"
        text = "#EDEDF5"
        muted = "#9494AC"
    else:
        bg = "#F5F6FA"
        panel = "#FFFFFF"
        card = "#FFFFFF"
        border = "#ECECF7"
        text = "#1F1F2E"
        muted = "#6B7280"

    primary = "#6C5CE7"
    primary_dark = "#5A4BD1"

    return f"""
<style>
:root {{
    --primary: {primary};
    --primary-dark: {primary_dark};
    --bg: {bg};
    --panel: {panel};
    --card: {card};
    --border: {border};
    --text: {text};
    --muted: {muted};
}}

.stApp {{
    background: var(--bg);
    color: var(--text);
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: var(--panel);
    border-right: 1px solid var(--border);
}}
[data-testid="stSidebar"] .stButton>button {{
    background: transparent;
    border: none;
    text-align: left;
    justify-content: flex-start;
    color: var(--text);
    font-weight: 500;
    padding: 0.4rem 0.6rem;
}}
[data-testid="stSidebar"] .stButton>button:hover {{
    background: var(--border);
    color: var(--primary);
}}

/* Generic cards (st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--card);
    border: 1px solid var(--border) !important;
    border-radius: 12px;
    padding: 0.25rem 0.25rem;
}}

/* Primary Send button */
.st-key-send_btn button {{
    background: var(--primary) !important;
    color: white !important;
    border: none !important;
    font-weight: 600;
    border-radius: 10px;
}}
.st-key-send_btn button:hover {{
    background: var(--primary-dark) !important;
}}

/* Document chips */
.st-key-chip_row .stButton>button {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 999px;
    font-size: 0.8rem;
    padding: 0.2rem 0.8rem;
    color: var(--text);
}}

/* Chat input row */
.st-key-ask_input_wrap input {{
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    background: var(--card) !important;
    color: var(--text) !important;
}}

/* Chat bubbles (st.chat_message) */
[data-testid="stChatMessage"] {{
    border-radius: 14px;
    padding: 0.4rem 0.6rem;
}}

/* Top bar buttons (Benchmarks / theme toggle) */
.st-key-top_benchmarks button, .st-key-top_theme button {{
    border-radius: 10px;
    border: 1px solid var(--border);
    background: var(--card);
    color: var(--text);
}}

hr {{
    border-color: var(--border) !important;
}}
</style>
"""