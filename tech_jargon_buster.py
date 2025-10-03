# tech_jargon_buster.py
"""
Tech Jargon Buster
------------------
A Streamlit-based chatbot that translates IT jargon into beginner-friendly language.

Developed by: Brock Frary
Date: 2025-10-02
Version: 0.3.0

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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    st.error("❌ Missing GITHUB_TOKEN in environment. Please set it in your .env file or Codespaces secrets.")
    st.stop()

# ========================
# API Endpoints + Models
# ========================
# GitHub Models (ChatGPT equivalent)
GITHUB_GPT_ENDPOINT = "https://models.inference.ai.azure.com/openai/deployments/gpt-4.1/chat/completions"
GITHUB_GPT_MODEL = "gpt-4.1"

# GitHub Models (Mistral Small)
GITHUB_MISTRAL_ENDPOINT = "https://models.github.ai/inference"
GITHUB_MISTRAL_MODEL = "mistral-small-2503"

# xAI Grok
GROK_ENDPOINT = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-3"

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
temperature = st.slider(
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
    "server", "api", "protocol", "firewall", "cloud", "database",
    "python", "encryption", "router", "algorithm", "token", "hash"
]

def is_it_term(term: str) -> bool:
    """Check if a term is IT-related by matching keywords."""
    term_lower = term.lower()
    return any(word in term_lower for word in IT_KEYWORDS)

# ========================
# GitHub Models GPT-4.1 Connector
# ========================
def call_github_gpt(term: str) -> str:
    """Call GitHub Models GPT-4.1 endpoint to explain IT jargon."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GITHUB_GPT_MODEL,
        "messages": [
            {"role": "system", "content": "You are an IT jargon explainer. Keep responses beginner-friendly."},
            {"role": "user", "content": f"Explain the IT jargon term '{term}' in simple language with a real-world analogy."}
        ],
        "temperature": 0.7
    }
    try:
        resp = requests.post(GITHUB_GPT_ENDPOINT, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error calling GitHub Models GPT-4.1: {e}"

# ========================
# GitHub Models Mistral 3B Connector
# ========================
def call_github_mistral(term: str) -> str:
    """Call GitHub Models Mistral Small 3.1 using Azure AI Inference SDK."""
    try:
        client = ChatCompletionsClient(
            endpoint="https://models.github.ai/inference",
            credential=AzureKeyCredential(GITHUB_TOKEN),
        )

        response = client.complete(
            messages=[
                SystemMessage("You are an IT jargon explainer. Keep responses beginner-friendly."),
                UserMessage(f"Explain the IT jargon term '{term}' with real-world analogies.")
            ],
            temperature=0.7,
            top_p=1.0,
            max_tokens=500,
            model="mistral-ai/mistral-small-2503"
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error calling GitHub Models Mistral Small 3.1: {e}"

# ========================
# xAI Grok Connector
# ========================
def call_grok(term: str) -> str:
    if not GROK_TOKEN:
        return "⚠️ xAI Grok integration unavailable (missing GROK_API_KEY)."

    headers = {
        "Authorization": f"Bearer {GROK_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROK_MODEL,
        "messages": [
            {"role": "system", "content": "Explain IT jargon in plain, beginner-friendly language."},
            {"role": "user", "content": f"Explain '{term}' with examples and analogies."}
        ]
    }
    try:
        resp = requests.post(GROK_ENDPOINT, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error calling xAI Grok-3: {e}"

# ========================
# Main Logic
# ========================
if submit:
    # TERM override allows bypassing IT keyword check
    if user_input.startswith("TERM:"):
        term = user_input.replace("TERM:", "").strip()
    else:
        if not is_it_term(user_input):
            st.warning("⚠️ The term entered is not considered a known IT term. Try again, or override with TERM:.")
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
        st.write(call_github_gpt(term))

    with col2:
        st.subheader("GitHub Models Mistral Small 3.1")
        st.write(call_github_mistral(term))

    with col3:
        st.subheader("xAI Grok-3")
        st.write(call_grok(term))





# © 2025 Brock Frary. All rights reserved.