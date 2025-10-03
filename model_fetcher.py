# model_fetcher

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Get GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("❌ Missing GITHUB_TOKEN. Please set it in your .env file or Codespaces secrets.")

# GitHub Models catalog endpoint
url = "https://models.github.ai/models"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/json"
}

try:
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    models = resp.json()

    print("✅ Models available to your GitHub token:\n")
    for model in models.get("data", []):
        print(f"- {model.get('id')} ({model.get('name')})")

except Exception as e:
    print(f"❌ Error retrieving models: {e}")
    if hasattr(e, "response") and e.response is not None:
        print("Response:", e.response.text)
