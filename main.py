import streamlit as st
import time
import random

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="spearBot",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# CUSTOM CSS
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* App background */
    .stApp {
        background: linear-gradient(160deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    /* Hide default streamlit chrome */
    #MainMenu, header, footer {visibility: hidden;}

    /* Header banner */
    .chat-header {
        text-align: center;
        padding: 2.2rem 1rem 1.6rem 1rem;
        margin-bottom: 1rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #0d1b3e 0%, #142a5c 55%, #0d1b3e 100%);
        box-shadow: 0 8px 28px rgba(0,0,0,0.45);
        border: 1px solid rgba(0, 212, 255, 0.25);
    }
    .chat-header h1 {
        color: #ffffff;
        background: linear-gradient(90deg, #00d4ff, #ffd166);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 4px 20px rgba(0, 212, 255, 0.25);
    }
    .chat-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        letter-spacing: 0.3px;
    }

    /* Chat bubbles - base style applies to EVERY message so text is always
       legible even in browsers that don't support :has() */
    div[data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.07) !important;
        border-radius: 16px !important;
        padding: 0.9rem 1.1rem !important;
        margin-bottom: 0.7rem !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
    }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessageContent"] * {
        color: #f4f4f5 !important;
    }

    /* User bubble tint (enhancement where :has() is supported) */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #7f5af0, #6246ea) !important;
        margin-left: 10%;
    }

    /* Assistant bubble tint */
    div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        background: rgba(255,255,255,0.06) !important;
        margin-right: 10%;
    }

    /* Fixed bottom bar that wraps the chat input (default is white) */
    [data-testid="stBottom"] {
        background: transparent !important;
    }
    [data-testid="stBottom"] > div {
        background: linear-gradient(180deg, rgba(15,12,41,0) 0%, #16213e 45%) !important;
    }
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }

    /* Chat input box */
    .stChatInput {
        background: transparent !important;
    }
    .stChatInput textarea, .stChatInput > div {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
    }
    .stChatInput textarea {
        color: white !important;
    }
    .stChatInput textarea::placeholder {
        color: rgba(255,255,255,0.5) !important;
    }
    /* Send button inside chat input */
    .stChatInput button {
        background: linear-gradient(135deg, #7f5af0, #2cb67d) !important;
        border-radius: 10px !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] * {
        color: #e4e4e7 !important;
    }
    /* Selectbox / dropdown */
    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(255,255,255,0.15) !important;
        color: #e4e4e7 !important;
    }
    div[data-baseweb="popover"] li {
        background: #1a1a2e !important;
        color: #e4e4e7 !important;
    }
    div[data-baseweb="popover"] li:hover {
        background: rgba(127, 90, 240, 0.3) !important;
    }
    /* Slider track/number */
    section[data-testid="stSidebar"] [data-testid="stSliderThumbValue"],
    section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
    section[data-testid="stSidebar"] [data-testid="stTickBarMax"] {
        color: #e4e4e7 !important;
    }

    /* Inline code / code blocks (e.g. `generate_response()`) */
    code {
        background: rgba(127, 90, 240, 0.18) !important;
        color: #c4b5fd !important;
        border: 1px solid rgba(127, 90, 240, 0.3);
        border-radius: 5px;
        padding: 0.1rem 0.4rem;
    }
    pre, pre code {
        background: rgba(0,0,0,0.3) !important;
        color: #e4e4e7 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        border: none;
        background: linear-gradient(135deg, #7f5af0, #2cb67d);
        color: white;
        font-weight: 600;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(127, 90, 240, 0.4);
        color: white;
    }

    /* Suggestion chips */
    .suggestion-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 20px;
        background: rgba(255,255,255,0.08);
        color: #e4e4e7;
        font-size: 0.85rem;
        border: 1px solid rgba(255,255,255,0.12);
        cursor: pointer;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: rgba(127, 90, 240, 0.5); border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💡 About")
    st.caption("An AI-powered assistant that enables employees to instantly search, understand, and navigate Deutsche Bank policies, procedures, and internal knowledge resources. Swap `generate_response()` with your own LLM call (OpenAI, Anthropic, local model, etc.).")
    st.markdown("---")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.markdown("""
<div class="chat-header">
    <h1>SPEARBot</h1>
    <p>Ask me anything about Deutsche Bank — I'm here to help.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ----------------------------------------------------------------------------
# MOCK RESPONSE GENERATOR — replace with your real API call
# ----------------------------------------------------------------------------
def generate_response(user_input: str) -> str:
    """
    Replace this function's body with a real call, e.g.:

    from anthropic import Anthropic
    client = Anthropic(api_key="...")
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "m", "content": user_input}]
    )
    return resp.content[0].text
    """
    canned = [
        f"That's an interesting point about \"{user_input[:40]}...\" — here's my take.",
        "Great question! Let me break that down for you.",
        "I'd be happy to help with that. Here's what I think:",
    ]
    return random.choice(canned) + "\n\n(This is a placeholder response — connect your model in `generate_response()`.)"

# ----------------------------------------------------------------------------
# WELCOME / SUGGESTION CHIPS (only when conversation is empty)
# ----------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown("<div style='text-align:center; color:#a1a1aa; margin-bottom:1rem;'>Try asking:</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    suggestions = ["⚖️ Explain employee code of conduct", "🏦 Tell me about Deutsche Bank", "📄 Show the leave policy"]
    for col, s in zip(cols, suggestions):
        with col:
            if st.button(s, use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": s.split(" ", 1)[1]})
                st.rerun()

# ----------------------------------------------------------------------------
# RENDER CHAT HISTORY
# ----------------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# If last message is from user (e.g. via chip click), generate a response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_text = generate_response(st.session_state.messages[-1]["content"])
        streamed = ""
        for word in full_text.split(" "):
            streamed += word + " "
            placeholder.markdown(streamed + "▌")
            time.sleep(0.02)
        placeholder.markdown(full_text)
    st.session_state.messages.append({"role": "assistant", "content": full_text})

# ----------------------------------------------------------------------------
# CHAT INPUT
# ----------------------------------------------------------------------------
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()