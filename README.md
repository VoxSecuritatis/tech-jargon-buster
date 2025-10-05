# Repository: Tech Jargon Buster
Published: 2025-10-02 | Updated: 2025-10-04

### Project page:  [Project page](https://github.com/VoxSecuritatis/Project-AI-tech-jargon-buster)
- Project page contains a 'Development timeline' of screenshots including the final UI if the Streamlit cloud app does not work (i.e., an API key restriction, rate limiting, etc.)

A **Streamlit** app that translates IT jargon into beginner-friendly explanations with real-world analogies.  
It queries **multiple LLMs via GitHub Models** to give side-by-side answers.

> Models used (via a single GitHub PAT):
> - **GitHub Models GPT-4.1**
> - **Mistral Small 3.1** (mistral-ai/mistral-small-2503)
> - **xAI Grok-3** (xai/grok-3)

---

## ✨ Features

- Plain-English explanations of IT/security terms with examples and analogies.
- **Three parallel responses** (GPT-4.1, Mistral, Grok-3) in a **horizontal layout**.
- **Creativity slider** (temperature) shared by all models.
- Built-in IT keyword detection with an **override**: `TERM:<your term>`.
- Works locally (Codespaces/desktop) and can be deployed to **Streamlit Community Cloud**.

---

## 📦 Requirements

- Python **3.9+** (tested in Codespaces with 3.12+).
- GitHub **Personal Access Token (PAT)** with **`models:read`** scope.
- The following Python packages (see `requirements.txt`):
  - `streamlit`
  - `requests`
  - `python-dotenv`
  - `azure-ai-inference` (SDK used for Mistral & Grok; on some platforms you may need a **beta** version like `1.0.0b9`)
  - `azure-core`

Example `requirements.txt`:

```txt
streamlit==1.39.0
requests==2.32.3
python-dotenv==1.0.1
azure-ai-inference==1.0.0b9
azure-core>=1.30.0
```

> If deployment complains about `azure-ai-inference==1.0.0` not found, switch to a published beta as shown above or unpin the exact version.

---

## 🔑 Configuration (Secrets)

The app expects a GitHub PAT in **`GITHUB_API_KEY`**. You can provide it in either place:

### Option A — `.env` (local/Codespaces)
Create a file at `./.env`:

```env
GITHUB_API_KEY=github_pat_xxxxxxxxxxxxxxxxxxxxxxxxx
```

The app loads this with:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option B — `.streamlit/secrets.toml` (local or Streamlit Cloud)
Create `./.streamlit/secrets.toml`:

```toml
GITHUB_API_KEY = "github_pat_xxxxxxxxxxxxxxxxxxxxxxxxx"
```

In code, the app falls back to:
```python
import streamlit as st
st.secrets.get("GITHUB_API_KEY")
```

**.gitignore** should include:
```
.env
.streamlit/secrets.toml
```

---

## 🧱 Project Structure (minimal)

```
tech-jargon-buster/
├─ tech_jargon_buster.py        # Streamlit app
├─ requirements.txt
├─ .env                         # (local) GitHub PAT - do NOT commit
└─ .streamlit/
   └─ secrets.toml              # (local/Cloud) GitHub PAT - do NOT commit
```

---

## 🛠️ Setup (Local / Codespaces)

### 1) Clone & enter the repo
```bash
git clone https://github.com/VoxSecuritatis/tech-jargon-buster.git
cd tech-jargon-buster
```

### 2) (Recommended) Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate  # Windows PowerShell
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Add your PAT
- Put `GITHUB_API_KEY=...` into `.env` **or**
- Put it into `.streamlit/secrets.toml`.

### 5) Run
```bash
streamlit run tech_jargon_buster.py
```

Open the URL shown (usually http://localhost:8501).

---

## ☁️ Deploy to Streamlit Community Cloud (optional)

1. Make your GitHub repo **public** (required for free tier).
2. Go to **share.streamlit.io** → **New app**:
   - **Repository**: `VoxSecuritatis/tech-jargon-buster`
   - **Branch**: `main`
   - **Main file path**: `tech_jargon_buster.py`
3. In **App → Settings → Secrets**, add:
   ```
   GITHUB_API_KEY = "github_pat_xxxxxxxxxxxxxxxxx"
   ```
4. **Deploy**.

Streamlit version:  https://tech-jargon-buster.streamlit.app

---

## 💡 How to Use

1. Enter an IT term (e.g., `firewall`, `ids`, `vpn`, `sso`, `oauth`).
2. Adjust the **Creativity (temperature)** slider (lower = more deterministic, higher = more creative).
3. Click **Explain**.
4. Compare answers from **GPT-4.1**, **Mistral Small**, and **Grok-3** shown side-by-side.

**Override**: If the app flags your input as non-IT, prefix with:
```
TERM:quantum key distribution
```

---

## 🛡️ Troubleshooting

### 401 Unauthorized (all models)
- Your PAT is missing or invalid.  
  - Confirm your `.env` or `secrets.toml` exists and is correctly named.
  - Ensure your PAT includes **`models:read`**.
  - Fine-grained PATs can **expire** — generate a new one if needed.

Quick test inside Python:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GITHUB_API_KEY')[:10])"
```
Should print `github_pat`… (or the first 10 chars), not `None`.

### `azure-ai-inference` not found
- Use a published beta (e.g., `1.0.0b9`) or unpin the version in `requirements.txt`.

### Columns too narrow
- The app includes CSS to widen the Streamlit container. If needed, adjust the `max-width` in the injected `<style>`.

---

## 🔍 Notes on Model Calls

- **GPT-4.1**: REST via `requests` to the GitHub Models endpoint.  
- **Mistral Small 3.1** & **xAI Grok-3**: via `azure-ai-inference` `ChatCompletionsClient` against `https://models.github.ai/inference`.  
- All three share the **same PAT** (`GITHUB_API_KEY`) and the **same temperature** from the slider.

---

## 📚 Attribution

- Developed by: **Brock Frary**  
- Special thanks to **Jonathan Fernandes** (LinkedIn Learning) for inspiration and teaching.  
  Course reference:  
  https://github.com/LinkedInLearning/Creating-AI-Applications-with-Python-and-GitHub-Models-5214188/tree/main

This project was developed as part of **personal learning and portfolio building**.  
If you create derivative works, please retain this attribution and credit Brock Frary as the original author.

---

## 📄 License

© 2025 Brock Frary. All rights reserved.
