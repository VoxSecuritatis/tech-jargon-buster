"""
Tech Jargon Buster
------------------
A Streamlit-based chatbot that translates IT jargon into beginner-friendly language.

Developed by: Brock Frary
Date: 2025-10-02
Version: 0.5.0

Attribution:
This project was developed as part of personal learning and portfolio building.
If you create derivative works, please retain this attribution header.
Credit should be given to Brock Frary as the original author.

Special thanks to Jonathan Fernandes and his contribution to LinkedIn Learning. 
A super interesting and well taught class!  
https://github.com/LinkedInLearning/Creating-AI-Applications-with-Python-and-GitHub-Models-5214188/tree/main.  
This was a fun portfolio project!

Description:
- Connects to multiple GenAI LLMs:
    * GitHub Models GPT-4.1 (ChatGPT equivalent)
    * GitHub Models Mistral 3B
    * xAI Grok-3
- Explains IT terminology in plain language with analogies.
- Includes logic to detect IT-related terms, with override option via 'TERM:' prefix.
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

# ========================
# Load environment variables
# ========================
load_dotenv()
# First try .env (local dev), then fall back to Streamlit secrets (cloud)
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY") or st.secrets.get("GITHUB_API_KEY")
if not GITHUB_API_KEY:
    st.error("❌ Missing GITHUB_API_KEY. Please set it in .env (local) or in Streamlit secrets (cloud).")
    st.stop()

# ========================
# API Endpoints + Models
# ========================
# GitHub Models - ChatGPT
GITHUB_GPT_ENDPOINT = "https://models.inference.ai.azure.com/openai/deployments/gpt-4.1/chat/completions"
GITHUB_GPT_MODEL = "gpt-4.1"

# GitHub Models - Mistral Small
GITHUB_MISTRAL_ENDPOINT = "https://models.github.ai/inference"
GITHUB_MISTRAL_MODEL = "mistral-small-2503"

# GitHub Models -  xAI Grok
GITHUB_GROK_ENDPOINT = "https://models.github.ai/inference"
GITHUB_GROK_MODEL = "xai/grok-3"

# ========================
# Streamlit UI
# ========================
st.title("Tech Jargon Buster")

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1800px;   /* widen the full app container */
            padding-left: 2rem;
            padding-right: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

user_input = st.text_input("Enter an IT jargon term:")
# Add slider for temperature
slider_temperature = st.slider(
    "Creativity (temperature)",
    min_value=0.0,
    max_value=1.5,
    value=0.4,      # default value; 0.7 is standard
    step=0.1,
    help="Lower values = more focused. Higher values = more creative."
)
st.markdown("*Move the slider left for straightforward answers, or right for more creative ones.*")
submit = st.button("Explain")

# ========================
# Helper: Simple IT check
# ========================
IT_KEYWORDS = [
    "firewall", "router", "switch", "vpn", "ids", "ips", "siem", "soar", "mfa",
    "sso", "oidc", "saml", "ssl", "tls", "dns", "dhcp", "http", "https", "api",
    "sdk", "json", "xml", "html", "css", "javascript", "python", "java", "c++",
    "docker", "kubernetes", "vmware", "hypervisor", "cloud", "aws", "azure",
    "gcp", "linux", "windows", "unix", "kernel", "sql", "nosql", "mongodb",
    "postgresql", "mysql", "ssh", "ftp", "smtp", "imap", "oauth", "rest"
]

def is_it_term(term: str) -> bool:
    """Check if a term is IT-related by matching keywords."""
    term_lower = term.lower()
    return any(word in term_lower for word in IT_KEYWORDS)

# ========================
# GitHub Models ChatGPT-4.1 Connector
# ========================
def call_github_gpt(term: str, temperature: float) -> str:
    """Call GitHub Models GPT-4.1 endpoint to explain IT jargon."""
    headers = {
        "Authorization": f"Bearer {GITHUB_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GITHUB_GPT_MODEL,
        "messages": [
            {"role": "system", "content": "You are an IT jargon explainer. Keep responses beginner-friendly."},
            {"role": "user", "content": f"Explain the IT jargon term '{term}' in simple language with a real-world analogy."}
        ],
        "temperature": temperature
    }
    try:
        resp = requests.post(GITHUB_GPT_ENDPOINT, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error calling GitHub Models GPT-4.1: {e}"

# ========================
# GitHub Models Mistral Small 3.1 Connector
# ========================
def call_github_mistral(term: str, temperature: float) -> str:
    """Call GitHub Models Mistral Small 3.1 using Azure AI Inference SDK."""
    try:
        # --------- SAFETY GUARD ----------
        # Cap temperature within 0.0–1.0 since Mistral rejects higher values
        safe_temp = min(max(temperature, 0.0), 1.0)

        # Notify user if their chosen temperature exceeded Mistral's limit
        if temperature > 1.0:
            st.info("⚠️ Mistral model supports up to temperature 1.0 — adjusted automatically.")

        client = ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(GITHUB_API_KEY),
        )

        response = client.complete(
            messages=[
                SystemMessage("You are an IT jargon explainer. Keep responses beginner-friendly."),
                UserMessage(f"Explain the IT jargon term '{term}' with real-world analogies.")
            ],
            temperature=safe_temp,
            top_p=1.0,
            max_tokens=500,
            model="mistral-ai/mistral-small-2503"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error calling GitHub Models Mistral Small 3.1: {e}"

# =======================
# GitHub Models xAI Grok-3 Connector
# ========================
def call_grok(term: str, temperature: float) -> str:
    """Call GitHub Models xAI Grok-3 using Azure AI Inference SDK."""
    try:
        client = ChatCompletionsClient(
            endpoint=GITHUB_GROK_ENDPOINT,
            credential=AzureKeyCredential(GITHUB_API_KEY),
        )

        response = client.complete(
            messages=[
                SystemMessage("You are an IT jargon explainer. Keep responses beginner-friendly."),
                UserMessage(f"Explain the IT jargon term '{term}' with examples and analogies.")
            ],
            temperature=temperature,
            top_p=1.0,
            max_tokens=500,
            model=GITHUB_GROK_MODEL
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error calling GitHub Models xAI Grok-3: {e}"

# ========================
# Main Logic
# ========================
if submit:
    # TERM override allows bypassing IT keyword check
    if user_input.startswith("TERM:"):
        term = user_input.replace("TERM:", "").strip()
    else:
        if not is_it_term(user_input):
            st.warning("⚠️ The term entered is not considered a known IT term. Try again, or override with TERM:. For example:  TERM:FTP")
            st.stop()
        term = user_input.strip()

    st.write(f"### Explanations for: {term}")

# ========================
# UI layout
# ========================
    # Create 3 columns for horizontal layout
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("GitHub Models GPT-4.1")
        st.write(call_github_gpt(term, slider_temperature))

    with col2:
        st.subheader("GitHub Models Mistral Small 3.1")
        st.write(call_github_mistral(term, slider_temperature))

    with col3:
        st.subheader("xAI Grok-3")
        st.write(call_grok(term, slider_temperature))

# © 2025 Brock Frary. All rights reserved.