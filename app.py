
import os
import streamlit as st
import json

# --- OpenAI Python SDK (>=1.0) ---
try:
    from openai import OpenAI
except Exception as e:
    st.error("OpenAI SDK not found. Make sure 'openai' is in requirements.txt and installed.")
    raise

# ----- App Title -----
st.set_page_config(page_title="About‑Me Chat", page_icon="💬")
st.title("💬 About‑Me Chat (OpenAI + Streamlit)")
st.caption("A simple personal chat box that answers based on *your* profile.")

# ----- Sidebar: Profile settings -----
with st.sidebar:
    st.header("🧩 Your profile")
    st.write("Fill these fields — they prime the assistant about you.")
    name = st.text_input("Name", value="Angela Beesley")
    roles = st.text_input("Roles / Titles", value="R&D Engineering Lead; MBA candidate")
    orgs = st.text_input("Organisations / Sectors", value="Thermo Fisher Scientific; Scientific instrumentation; Aerospace actuators; Consumer goods")
    interests = st.text_input("Interests / Domains", value="Quantum readiness; AI & data; Operations & supply chain; Sustainability")
    achievements = st.text_area("Key achievements (bulleted)", value="- Led cross‑functional R&D teams\n- Designed analytics instrumentation improvements\n- MBA projects on quantum and supply chain")
    tone = st.selectbox("Tone", ["Professional", "Warm", "Crisp & concise", "Enthusiastic"], index=0)
    model_name = st.text_input("OpenAI model", value=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    temperature = st.slider("Creativity (temperature)", 0.0, 1.2, 0.4, 0.1)
    st.divider()
    st.write("**API key:** put `OPENAI_API_KEY` in Streamlit *secrets* or as an environment variable.")
    clear = st.button("🧹 Clear conversation")

if clear:
    st.session_state.pop("messages", None)

# ----- Build the system prompt from sidebar fields -----
profile_dict = {
    "name": name,
    "roles": roles,
    "organizations_sectors": orgs,
    "interests": interests,
    "achievements": achievements,
    "tone": tone,
}

SYSTEM_PROMPT = f'''
You are a helpful assistant that answers *as a concierge about the user*, using the profile below.
Use it to personalize answers (e.g., examples, wording, industries). If asked "about me", summarize from this profile.
If a question is outside the profile, answer normally but still try to anchor to the user's context when helpful.
Keep responses clear and structured. Avoid inventing facts not in the profile.

[USER PROFILE JSON]
{json.dumps(profile_dict, indent=2)}
'''

# ----- Session state for chat history -----
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

# If profile changed, refresh the system message
if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
    st.session_state.messages[0]["content"] = SYSTEM_PROMPT

# ----- Suggested prompts -----
with st.expander("✨ Try a suggested prompt"):
    cols = st.columns(2)
    examples = [
        "Summarize my background for a short professional bio.",
        "Draft a LinkedIn 'About' section using my profile.",
        "What strengths should I highlight for a Head of Engineering role?",
        "Create 5 interview questions I’m likely to get, with model answers.",
        "Write a 1‑paragraph intro tying my MBA to my R&D role.",
        "Outline a 90‑day plan for my next leadership step."
    ]
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex):
            st.session_state["prefill"] = ex

# ----- Chat rendering -----
for msg in st.session_state.messages[1:]:  # skip system
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

#user_input = st.chat_input("Ask something about you (or anything)…", key="chat_input", default=st.session_state.pop("prefill", ""))
user_input = st.chat_input("Ask something about you (or anything)…")


# ----- Call OpenAI -----
def call_openai(messages, model_name, temperature):
    api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        st.error("Missing OPENAI_API_KEY. Add it to .streamlit/secrets.toml or your environment.")
        st.stop()

    client = OpenAI(api_key=api_key)

    # OpenAI Chat Completions API
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return None

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            reply = call_openai(st.session_state.messages, model_name, temperature)
            if reply:
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
