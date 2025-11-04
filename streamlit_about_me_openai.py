# streamlit_about_me_openai.py
# Streamlit "About Me" chat that answers using OpenAI, grounded ONLY in your profile.

import json
import os
import pathlib
import streamlit as st
from openai import OpenAI

# ----------------------- 1) CONFIG -------------------------------------------
st.set_page_config(page_title="About-Me Chat", page_icon="💬", layout="centered")

# Load secrets / API
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
if not api_key:
    st.warning("Add your OPENAI_API_KEY in Streamlit Secrets or environment variables to enable answers.")
client = OpenAI(api_key=api_key)

MODEL = st.secrets.get("OPENAI_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

# ----------------------- 2) YOUR PROFILE -------------------------------------
# You can edit here OR provide a profile.json next to this file with the same keys.
DEFAULT_PROFILE = {
    "name": "Your Name",
    "headline": "Engineering Lead in Scientific Instrumentation",
    "location": "Winsford, UK",
    "employer": "Thermo Fisher Scientific",
    "education": "MBA, University of Wolverhampton",
    "interests": [
        "quantum computing", "instrumentation", "leadership", "sustainability"
    ],
    "links": {
        "email": "you@example.com",
        "linkedin": "https://www.linkedin.com/in/your-handle/"
    },
    "fun_facts": [
        "Built a data dashboard that saved the team hours weekly."
    ],
    "topics_allowed": [
        "my role", "experience", "skills", "education",
        "interests", "location", "contact", "fun facts"
    ]
}

def load_profile():
    path = pathlib.Path(__file__).with_name("profile.json")
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            st.error(f"Could not read profile.json: {e}")
    return DEFAULT_PROFILE

PROFILE = load_profile()

# ----------------------- 3) SYSTEM PROMPT ------------------------------------
SYSTEM_PROMPT = f"""
You are an assistant that ONLY answers questions about the user's public profile below.
If a question is outside the profile, say you don't have that information.
Be concise, friendly, and truthful. If contact details are requested, share only what's in the profile.
Do not invent facts. If uncertain, say so.

PROFILE (JSON):
{json.dumps(PROFILE, ensure_ascii=False, indent=2)}
"""

# ----------------------- 4) UI -----------------------------------------------
st.title("💬 About-Me Chat")
st.caption("Powered by OpenAI • Answers grounded in your profile.json")

with st.expander("Preview profile"):
    st.json(PROFILE)

# Session state for chat
if "history" not in st.session_state:
    st.session_state.history = [
        {"role": "assistant", "content": "Hi! Ask me about my role, experience, interests, education, or how to contact me."}
    ]

# Chat display
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input box
user_input = st.chat_input("Ask about me (e.g., 'What do you do?' or 'How can I contact you?')")

def call_openai(messages):
    """Call OpenAI Chat Completions."""
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.4,
        messages=messages,
    )
    return resp.choices[0].message.content

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if not api_key:
        bot_reply = "I can't answer until an OpenAI API key is configured."
    else:
        # Build full message context with a strict system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(st.session_state.history)  # includes past turns
        bot_reply = call_openai(messages)

    st.session_state.history.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

st.divider()
st.caption("Tip: Put your details in a local **profile.json** next to this file to update answers without editing code.")
