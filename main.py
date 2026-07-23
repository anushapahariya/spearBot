import streamlit as st
import time
import json
import uuid
from pathlib import Path

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="SpearBot",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# PERSISTENCE
# ----------------------------------------------------------------------------
HISTORY_FILE = Path(__file__).parent / "chat_history.json"

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_history(history: dict):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

def make_title(messages: list) -> str:
    for m in messages:
        if m["role"] == "user":
            return (m["content"][:40] + "…") if len(m["content"]) > 40 else m["content"]
    return "New chat"

# ----------------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = load_history()

if "current_id" not in st.session_state:
    if st.session_state.history:
        st.session_state.current_id = list(st.session_state.history.keys())[-1]
    else:
        new_id = str(uuid.uuid4())
        st.session_state.history[new_id] = {"title": "New chat", "messages": []}
        st.session_state.current_id = new_id

# ----------------------------------------------------------------------------
# CSS — never hide header, never hide sidebar arrows
# ----------------------------------------------------------------------------
# Theme support: light and dark CSS
# Initialize theme in session state early so CSS selection works
if "theme" not in st.session_state:
    st.session_state.theme = "light"

light_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* App background: light, soft neutrals */
    .stApp {
        background: linear-gradient(160deg, #f8fafc 0%, #eef2f7 50%, #f8fafc 100%);
        color: #0f172a;
    }

    /* Only hide the hamburger menu and footer — NOT the header */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Header: subtle translucent white */
    header[data-testid="stHeader"] {
        background: rgba(255,255,255,0.9) !important;
        box-shadow: 0 1px 8px rgba(15, 23, 42, 0.06) !important;
        border-bottom: 1px solid rgba(15,23,42,0.04) !important;
    }

    /* Make sidebar collapse/expand arrows visible for light background */
    [data-testid="stSidebarCollapseButton"] svg { fill: #0f172a !important; }
    [data-testid="collapsedControl"] svg       { fill: #0f172a !important; }

    /* Chat header banner */
    .chat-header {
        text-align: center;
        padding: 2.2rem 1rem 1.6rem 1rem;
        margin-bottom: 1rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #ffffff 0%, #f1f5f9 55%, #ffffff 100%);
        box-shadow: 0 6px 20px rgba(15,23,42,0.04);
        border: 1px solid rgba(15,23,42,0.04);
    }
    .chat-header h1 {
        background: linear-gradient(90deg, #334155, #0f172a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    .chat-header p {
        color: rgba(15,23,42,0.75);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }

    /* Chat bubbles (light) */
    div[data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.9) !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.1rem !important;
        margin-bottom: 0.7rem !important;
        border: 1px solid rgba(15,23,42,0.06) !important;
        box-shadow: 0 4px 12px rgba(15,23,42,0.03);
    }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessageContent"] * {
        color: #0f172a !important;
    }
    /* User message (light accent) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #e0f2fe, #bae6fd) !important;
        border: 1px solid rgba(56,189,248,0.25) !important;
        margin-left: 10%;
    }
    /* Assistant message */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, #f8fafc, #f1f5f9) !important;
        border: 1px solid rgba(15,23,42,0.04) !important;
        margin-right: 10%;
    }

    /* Bottom bar */
    [data-testid="stBottom"] { background: transparent !important; }
    [data-testid="stBottom"] > div {
        background: linear-gradient(180deg, rgba(255,255,255,0) 0%, #f8fafc 45%) !important;
    }
    [data-testid="stBottomBlockContainer"] { background: transparent !important; }

    /* Chat input - enhanced */
    .stChatInput { background: transparent !important; padding: 0.6rem 0 !important; }
    .stChatInput textarea, .stChatInput > div {
        border-radius: 20px !important;
        background: linear-gradient(180deg, #ffffff, #f8fafc) !important;
        border: 1px solid rgba(15,23,42,0.06) !important;
        padding: 0.85rem 1rem !important;
        box-shadow: 0 6px 18px rgba(16,24,40,0.03) inset, 0 6px 18px rgba(16,24,40,0.02);
        transition: box-shadow 0.15s ease, transform 0.08s ease;
        resize: none !important;
    }
    .stChatInput textarea:focus, .stChatInput > div:focus-within {
        box-shadow: 0 10px 26px rgba(96,165,250,0.12), 0 2px 6px rgba(16,24,40,0.06) inset !important;
        outline: none !important;
        transform: translateY(-1px);
    }
    .stChatInput textarea { color: #0f172a !important; font-size: 1rem !important; line-height:1.4 !important; }
    .stChatInput textarea::placeholder { color: rgba(15,23,42,0.35) !important; font-style:italic; }
    .stChatInput button {
        background: linear-gradient(135deg, #06b6d4, #2563eb) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 0.6rem 0.9rem !important;
        box-shadow: 0 6px 18px rgba(6,182,212,0.12);
        border: none !important;
        font-weight:700 !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stChatInput button:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(6,182,212,0.18); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid rgba(15,23,42,0.04);
    }
    section[data-testid="stSidebar"] * { color: #0f172a !important; }

    /* Main area buttons */
    .stButton > button {
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #60a5fa, #93c5fd);
        color: #04294a !important;
        font-weight: 600;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(16,24,40,0.06);
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        text-align: left !important;
        justify-content: flex-start !important;
        background: transparent !important;
        color: #0f172a !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        padding: 0.4rem 0.6rem !important;
        border-radius: 8px !important;
        transform: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(96,165,250,0.08) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(1) > button {
        background: linear-gradient(135deg, #e6f4ff, #dbeafe) !important;
        color: #04294a !important;
        font-weight: 700 !important;
        text-align: center !important;
        justify-content: center !important;
        padding: 0.6rem !important;
        border: 1px solid rgba(96,165,250,0.16) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(2) > button {
        background: linear-gradient(135deg, #fee2e2, #fecaca) !important;
        color: #04294a !important;
        font-weight: 700 !important;
        text-align: center !important;
        justify-content: center !important;
        padding: 0.6rem !important;
        border: 1px solid rgba(239,68,68,0.12) !important;
    }

    /* Code */
    code {
        background: rgba(15,23,42,0.04) !important;
        color: #0f172a !important;
        border-radius: 5px;
        padding: 0.1rem 0.4rem;
    }
    pre, pre code {
        background: rgba(15,23,42,0.02) !important;
        color: #0f172a !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: rgba(15,23,42,0.12); border-radius: 8px; }
</style>
"""

# A compact dark theme that mirrors the previous dark styling
dark_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* App background */
    .stApp { background: linear-gradient(160deg, #070617 0%, #0b1028 45%, #0e1226 100%); color: #e6eef2; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Header */
    header[data-testid="stHeader"] { background: rgba(6,7,25,0.75) !important; box-shadow: 0 6px 18px rgba(2,6,23,0.6) !important; border-bottom: 1px solid rgba(96,165,250,0.06) !important; }
    [data-testid="stSidebarCollapseButton"] svg { fill: #e6eef2 !important; }
    [data-testid="collapsedControl"] svg       { fill: #e6eef2 !important; }

    /* Chat header banner */
    .chat-header {
        text-align:center; padding:2.2rem 1rem 1.6rem 1rem; margin-bottom:1rem; border-radius:18px;
        background: linear-gradient(120deg, rgba(10,16,40,0.85) 0%, rgba(15,25,55,0.85) 55%, rgba(10,16,40,0.85) 100%);
        box-shadow: 0 10px 36px rgba(2,6,23,0.7); border: 1px solid rgba(96,165,250,0.16);
    }
    .chat-header h1 { background: linear-gradient(90deg, #58f0ff, #ffd166); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:3.2rem; font-weight:800; margin:0; }
    .chat-header p { color: rgba(230,238,242,0.9); margin:0.5rem 0 0 0; }

    /* Chat bubbles - higher contrast */
    div[data-testid="stChatMessage"] {
        background: rgba(10,14,25,0.7) !important; border-radius:16px !important; padding:0.9rem 1.1rem !important; margin-bottom:0.9rem !important;
        border:1px solid rgba(255,255,255,0.04) !important; box-shadow:0 8px 24px rgba(2,6,23,0.65);
    }
    div[data-testid="stChatMessage"] p, div[data-testid="stChatMessage"] span, div[data-testid="stChatMessage"] li, div[data-testid="stChatMessage"] div, div[data-testid="stChatMessageContent"] * { color: #e6eef2 !important; }

    /* User message - warm accent */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #ffedd5, #ffd7a8) !important; color: #0b1220 !important; border:1px solid rgba(249,115,22,0.18) !important; margin-left:8% !important;
    }

    /* Assistant message - cool accent */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, rgba(6,182,212,0.12), rgba(20,83,255,0.08)) !important;
        border: 1px solid rgba(6,182,212,0.28) !important; color: #e6eef2 !important; margin-right:8% !important;
    }

    /* Bottom bar */
    [data-testid="stBottom"] { background: transparent !important; }
    [data-testid="stBottom"] > div { background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(3,6,20,0.6) 45%) !important; }
    [data-testid="stBottomBlockContainer"] { background: transparent !important; }

    /* Chat input - enhanced for dark */
    .stChatInput { background: transparent !important; padding: 0.6rem 0 !important; }
    .stChatInput textarea, .stChatInput > div {
        border-radius: 20px !important; background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)) !important;
        border: 1px solid rgba(96,165,250,0.10) !important; padding: 0.85rem 1rem !important;
        box-shadow: 0 10px 30px rgba(2,6,23,0.7) inset, 0 6px 18px rgba(96,165,250,0.03);
        transition: box-shadow 0.15s ease, transform 0.08s ease; resize: none !important;
    }
    .stChatInput textarea:focus, .stChatInput > div:focus-within {
        box-shadow: 0 14px 40px rgba(20,83,255,0.14), 0 3px 8px rgba(2,6,23,0.6) inset !important; outline: none !important; transform: translateY(-1px);
    }
    .stChatInput textarea { color: #e6eef2 !important; font-size: 1rem !important; line-height:1.4 !important; }
    .stChatInput textarea::placeholder { color: rgba(230,238,242,0.38) !important; font-style:italic; }

    /* Send button - vivid */
    .stChatInput button {
        background: linear-gradient(135deg, #06b6d4, #60a5fa) !important;
        border-radius: 14px !important; color: #02121a !important; padding: 0.6rem 0.95rem !important;
        box-shadow: 0 10px 30px rgba(6,182,212,0.14); border: none !important; font-weight:800 !important; transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stChatInput button:hover { transform: translateY(-3px); box-shadow: 0 18px 44px rgba(96,165,250,0.2); }

    /* Sidebar - more distinct */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #071026 0%, #07122a 100%); border-right: 1px solid rgba(96,165,250,0.08); }
    section[data-testid="stSidebar"] * { color: #e6eef2 !important; }

    /* Sidebar primary button (New chat) */
    section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(1) > button {
        background: linear-gradient(135deg, #0ea5b7, #06b6d4) !important; color: #02121a !important; font-weight:700 !important; padding: 0.6rem !important; border-radius:12px !important; border: 1px solid rgba(6,182,212,0.12) !important;
    }
    /* Sidebar delete button */
    section[data-testid="stSidebar"] div[data-testid="stButton"]:nth-of-type(2) > button {
        background: linear-gradient(135deg, #fb7185, #ef4444) !important; color: #02121a !important; font-weight:700 !important; padding: 0.6rem !important; border-radius:12px !important; border: 1px solid rgba(239,68,68,0.12) !important;
    }
    /* Sidebar other buttons */
    section[data-testid="stSidebar"] .stButton > button { background: transparent !important; color: #cfe9f5 !important; font-weight:500 !important; }
    section[data-testid="stSidebar"] .stButton > button:hover { background: rgba(96,165,250,0.08) !important; }

    /* Main area buttons */
    .stButton > button { border-radius:10px; border:none; background: linear-gradient(135deg, #06b6d4, #60a5fa); color:#02121a !important; font-weight:700; box-shadow: 0 8px 24px rgba(6,182,212,0.08); }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 18px 44px rgba(6,182,212,0.14); }

    /* Code */
    code { background: rgba(0,0,0,0.45) !important; color: #7dd3fc !important; }
    pre, pre code { background: rgba(2,6,23,0.85) !important; color: #e6eef2 !important; border-radius:8px; padding:0.6rem; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg,#374151,#111827); border-radius: 8px; }
</style>
"""

css_to_inject = dark_css if st.session_state.theme == "dark" else light_css
st.markdown(css_to_inject, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💡 About")
    st.caption("An AI-powered assistant that enables employees to instantly search, understand, and navigate Deutsche Bank policies, procedures, and internal knowledge resources.")
    st.markdown("---")

    # Theme selector
    st.markdown("### Theme")
    tcols = st.columns(2)
    if tcols[0].button("Light", use_container_width=True):
        st.session_state.theme = "light"
        st.rerun()
    if tcols[1].button("Dark", use_container_width=True):
        st.session_state.theme = "dark"
        st.rerun()

    st.markdown("---")

    if st.button("➕  New chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.history[new_id] = {"title": "New chat", "messages": []}
        st.session_state.current_id = new_id
        save_history(st.session_state.history)
        st.rerun()

    if st.button("🗑️ Delete this chat", use_container_width=True):
        del st.session_state.history[st.session_state.current_id]
        if not st.session_state.history:
            new_id = str(uuid.uuid4())
            st.session_state.history[new_id] = {"title": "New chat", "messages": []}
            st.session_state.current_id = new_id
        else:
            st.session_state.current_id = list(st.session_state.history.keys())[-1]
        save_history(st.session_state.history)
        st.rerun()

    st.markdown("---")
    st.markdown("**Recent chats**")

    for conv_id in reversed(list(st.session_state.history.keys())):
        conv = st.session_state.history[conv_id]
        label = ("📍 " if conv_id == st.session_state.current_id else "") + conv["title"]
        if st.button(label, key=f"conv_{conv_id}", use_container_width=True):
            st.session_state.current_id = conv_id
            st.rerun()

# ----------------------------------------------------------------------------
# MAIN AREA
# ----------------------------------------------------------------------------
messages = st.session_state.history[st.session_state.current_id]["messages"]

st.markdown("""
<div class="chat-header">
    <h2>SpearBot</h2>
    <p>Ask me anything about Deutsche Bank — I'm here to help.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# RESPONSE GENERATOR
# ----------------------------------------------------------------------------
def generate_response(user_input: str) -> str:
    import requests
    try:
        response = requests.post(
            "https://your-backend-api.com/chat",
            json={"message": user_input},
            headers={"Authorization": "Bearer YOUR_API_KEY"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["reply"]
    except Exception as e:
        return f"⚠️ Error contacting backend: {e}"

# ----------------------------------------------------------------------------
# SUGGESTION CHIPS
# ----------------------------------------------------------------------------
if not messages:
    st.markdown("<div style='text-align:center; color:#a1a1aa; margin-bottom:1rem;'>Try asking:</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    suggestions = ["⚖️ Explain employee code of conduct", "🏦 Tell me about Deutsche Bank", "📄 Show the leave policy"]
    for col, s in zip(cols, suggestions):
        with col:
            if st.button(s, use_container_width=True):
                messages.append({"role": "user", "content": s.split(" ", 1)[1]})
                st.rerun()

# ----------------------------------------------------------------------------
# RENDER CHAT HISTORY
# ----------------------------------------------------------------------------
for msg in messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if messages and messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_text = generate_response(messages[-1]["content"])
        streamed = ""
        for word in full_text.split(" "):
            streamed += word + " "
            placeholder.markdown(streamed + "▌")
            time.sleep(0.02)
        placeholder.markdown(full_text)
    messages.append({"role": "assistant", "content": full_text})
    st.session_state.history[st.session_state.current_id]["title"] = make_title(messages)
    save_history(st.session_state.history)

# ----------------------------------------------------------------------------
# CHAT INPUT
# ----------------------------------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    messages.append({"role": "user", "content": prompt})
    save_history(st.session_state.history)
    st.rerun()
