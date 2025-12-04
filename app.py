import os
import json
from pathlib import Path

import streamlit as st
from openai import OpenAI

# ========== CONFIG ==========
BASE_DIR = Path(__file__).parent
KB_PATH = BASE_DIR / "kb.md"                     # markdown knowledge base
JSON_PATH = BASE_DIR / "Angela_Beesley_CV.json"  # structured CV/profile JSON
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

st.set_page_config(page_title="Angela – Interview Chat", page_icon="💬")
st.title("💬 Interview Chat with Angela (AI Twin)")
st.caption(
    "Interview-style assistant that answers in the first person based on my professional profile. "
    "For formal enquiries or clarifications, please contact me directly via LinkedIn."
)

# ========== LOAD KNOWLEDGE BASE & JSON PROFILE ==========

def load_kb(path: Path) -> str:
    if not path.exists():
        st.warning(f"Knowledge base file not found: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        st.error(f"Could not read knowledge base file: {e}")
        return ""

def load_json_profile(path: Path):
    if not path.exists():
        st.warning(f"JSON profile file not found: {path}")
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception as e:
        st.error(f"Could not parse JSON file: {e}")
        return {}

kb_text = load_kb(KB_PATH)
cv_data = load_json_profile(JSON_PATH)
cv_json_str = json.dumps(cv_data, indent=2, ensure_ascii=False) if cv_data else "{}"

# ========== SYSTEM PROMPT (NO USER INPUT NEEDED) ==========

SYSTEM_PROMPT = f"""
You are an AI "twin" of **Dr Angela Beesley**.

Your job:
- Answer questions in an interview style, in the **first person** (using "I").
- Imagine the user is an interviewer asking about my background, experience, skills, leadership style, etc.
- Always base your answers on the knowledge base and JSON profile below.
- If you are not sure about a detail, be honest and avoid inventing facts.

Tone:
- Professional, clear, and confident.
- Where useful, give concise examples from my experience.

[KNOWLEDGE BASE: kb.md]
{kb_text}

[STRUCTURED PROFILE: Angela_Beesley_CV.json]
{cv_json_str}
"""

# ========== OPENAI CLIENT HELPERS ==========

def get_client():
    api_key = st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, "secrets") else None
    api_key = api_key or os.environ.get("OPENAI_API_KEY")

    if not api_key:
        st.error(
            "OPENAI_API_KEY is not set. "
            "Set it as an environment variable or in Streamlit secrets."
        )
        st.stop()

    return OpenAI(api_key=api_key)

def call_openai(messages, model_name: str = DEFAULT_MODEL, temperature: float = 0.5):
    client = get_client()

    # Some models might not support non-default temperature; handle gracefully.
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
        )
        return completion.choices[0].message.content
    except Exception as e:
        if "temperature" in str(e).lower():
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                )
                return completion.choices[0].message.content
            except Exception as e2:
                st.error(f"OpenAI error (retry without temperature): {e2}")
                return None
        st.error(f"OpenAI error: {e}")
        return None

# ========== SESSION STATE (CHAT HISTORY) ==========

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Always keep system prompt up to date
if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
    st.session_state.messages[0]["content"] = SYSTEM_PROMPT

# ========== SUGGESTED INTERVIEW QUESTIONS ==========

suggested_questions = [
    "Can you give me a concise overview of your career to date?",
    "How has your experience in aerospace influenced your current R&D leadership role?",
    "What are your key strengths as a Head of Engineering or R&D leader?",
    "Can you describe a complex project you led and how you managed risk and compliance?",
    "How do you approach mentoring and developing engineering teams?",
    "How does your MBA complement your technical background and leadership style?",
]

with st.expander("✨ Suggested interview questions"):
    cols = st.columns(2)
    for i, q in enumerate(suggested_questions):
        if cols[i % 2].button(q, key=f"sugg_{i}"):
            # Store the clicked question as "pending" and trigger a rerun
            st.session_state["pending_submit"] = q
            st.rerun()

# ========== CHAT UI (NO SIDEBAR, ALWAYS SHOW INPUT) ==========

# 1. Chat input box (always visible)
box_input = st.chat_input("Ask an interview question…")

# 2. If a suggested question was clicked and user didn't type anything, submit that
pending = st.session_state.pop("pending_submit", None)
if pending and not box_input:
    user_input = pending
else:
    user_input = box_input

# 3. Render conversation history (excluding system)
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. If there is user input (typed or suggested), send to OpenAI
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = call_openai(st.session_state.messages)
            if reply:
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )
