# smoke_test.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("❌ Missing GITHUB_TOKEN")

endpoint = "https://models.github.ai/inference"
test_models = [
    "gpt-4.1",
    "gpt-4o-mini",
    "mistral-ai/Ministral-3B",  # may 404
    "anthropic/claude-3-5-sonnet"  # example: GitHub may support Anthropic
]

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

for model in test_models:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Say only OK if you are alive."}
        ],
        "max_tokens": 10
    }
    print(f"\n🔎 Testing model: {model}")
    try:
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        print("✅ Available:", resp.json()["choices"][0]["message"]["content"])
    except Exception as e:
        print("❌ Not available:", e)
        if hasattr(e, "response") and e.response is not None:
            print("Response:", e.response.text)
