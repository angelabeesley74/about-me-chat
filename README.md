# About‑Me Chat (Streamlit + OpenAI)

A minimal Streamlit chat box that answers *about you* by using a small profile you fill in the sidebar.

## 1) Setup

### A. Create a virtual environment (optional but recommended)
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### B. Install dependencies
```bash
pip install -r requirements.txt
```

### C. Provide your OpenAI API key
**Option 1: Streamlit secrets (recommended)**

Create a file at:
- Windows: `%USERPROFILE%\.streamlit\secrets.toml`
- macOS/Linux: `~/.streamlit/secrets.toml`

Put this inside:
```toml
OPENAI_API_KEY = "sk-REPLACE_ME"
```

**Option 2: Environment variable**

- Windows (new terminal after running):
```powershell
setx OPENAI_API_KEY "sk-REPLACE_ME"
```

- macOS/Linux:
```bash
export OPENAI_API_KEY="sk-REPLACE_ME"
```

> If you previously saw `StreamlitSecretNotFoundError`, it means your `secrets.toml` was missing. Create it as above.

## 2) Run locally
```bash
streamlit run app.py
```

## 3) Deploy (optional)
- **Streamlit Community Cloud**: push these files to a public GitHub repo, then click *New app* and paste the repo link. In the app's menu → **Edit secrets**, paste the same TOML block with your key.
- **Other hosts**: set `OPENAI_API_KEY` as an environment variable or secret as per your platform.

## Notes
- You can change the model in the sidebar. Defaults to `gpt-5-mini` (adjust to what your account has access to).
- The app uses the official OpenAI Python SDK (>=1.0) and the Chat Completions API.
