# ==========================================================
# model_fetcher.py
# ----------------------------------------------------------
# Purpose:
#   Validate connectivity to GitHub Models endpoints
#   (GPT-4.1, Mistral Small 3.1, and xAI Grok-3)
#
# Developed by: Brock Frary
# Version: 0.6.0
# Date: 2025-10-04
# ==========================================================

import os
import requests
from dotenv import load_dotenv

# -----------------------------
# Load API Key from .env
# -----------------------------
load_dotenv()
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")

if not GITHUB_API_KEY:
    raise ValueError("❌ Missing GITHUB_API_KEY. Please set it in your .env file or Codespaces secrets.")

# -----------------------------
# Define Endpoints
# -----------------------------
endpoints = {
    "GitHub GPT-4.1": "https://models.inference.ai.azure.com/openai/deployments/gpt-4.1/chat/completions",
    "GitHub Mistral Small": "https://api.github.ai/v1/chat/completions",
    "xAI Grok-3": "https://api.github.ai/v1/chat/completions",
    "GitHub Models Catalog": "https://models.inference.ai.azure.com/openai/models",
}

headers = {
    "Authorization": f"Bearer {GITHUB_API_KEY}",
    "Accept": "application/json"
}

# -----------------------------
# Check each endpoint (HEAD/GET)
# -----------------------------
print("🔍 Checking GitHub Models API endpoints...\n")

for name, url in endpoints.items():
    try:
        # For chat/completions, use HEAD to avoid triggering a real completion
        method = "HEAD" if "completions" in url else "GET"
        resp = requests.request(method, url, headers=headers, timeout=15)
        status = resp.status_code

        if status == 200:
            print(f"✅ {name} is reachable ({status})")
        elif status in (401, 403):
            print(f"🔒 {name} – Unauthorized ({status}). Check your GITHUB_API_KEY permissions.")
        elif status in (404, 405):
            print(f"⚠️ {name} – Endpoint exists but may require POST instead of GET/HEAD ({status}).")
        else:
            print(f"⚠️ {name} returned unexpected status: {status}")

    except requests.exceptions.RequestException as e:
        print(f"❌ {name} – Error: {e}")

# -----------------------------
# Optionally, list all models
# -----------------------------
try:
    print("\n📋 Retrieving available models from GitHub Models catalog...")
    url = "https://models.inference.ai.azure.com/openai/models"
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    models = resp.json()

    print("\n✅ Models available to your GitHub token:\n")
    for model in models.get("data", []):
        print(f"- {model.get('id')} ({model.get('object')})")

except Exception as e:
    print(f"\n❌ Error retrieving model catalog: {e}")

# -----------------------------
# Optional: Live POST tests for all models
# -----------------------------
print("\n🚀 Performing live completion tests on all GitHub Models endpoints...\n")

test_models = [
    {
        "name": "GitHub GPT-4.1",
        "endpoint": "https://models.inference.ai.azure.com/openai/deployments/gpt-4.1/chat/completions",
        "model": "gpt-4.1",
    },
    {
        "name": "Mistral Small 3.1",
        "endpoint": "https://models.inference.ai.azure.com/openai/deployments/mistral-small-2503/chat/completions",
        "model": "mistral-ai/mistral-small-2503",
    },
    {
        "name": "xAI Grok-3",
        "endpoint": "https://models.inference.ai.azure.com/openai/deployments/xai-grok-3/chat/completions",
        "model": "xai/grok-3",
    },
]

for tm in test_models:
    print(f"🧩 Testing {tm['name']} ...")
    try:
        test_headers = {
            "Authorization": f"Bearer {GITHUB_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        test_payload = {
            "model": tm["model"],
            "messages": [
                {"role": "user", "content": f"Say 'Connection OK' if you can read this. (Testing {tm['name']})"}
            ],
            "temperature": 0
        }

        response = requests.post(tm["endpoint"], headers=test_headers, json=test_payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            message = data["choices"][0]["message"]["content"]
            print(f"✅ {tm['name']} responded successfully:\n{message}\n")
        elif response.status_code in (401, 403):
            print(f"🔒 {tm['name']} – Unauthorized ({response.status_code}). Check GITHUB_API_KEY permissions.")
        elif response.status_code in (404, 405):
            print(f"⚠️ {tm['name']} – Endpoint exists but requires different deployment route ({response.status_code}).")
        else:
            print(f"⚠️ {tm['name']} returned {response.status_code}: {response.text[:300]}")

    except Exception as e:
        print(f"❌ Error testing {tm['name']}: {e}\n")

print("\n✅ Live inference tests complete.\n")
