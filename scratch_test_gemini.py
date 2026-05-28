import os
import requests
from campus_notice_crawler.utils.env_loader import load_project_env

load_project_env()
gemini_key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", gemini_key)

models = ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
    payload = {
        "contents": [{
            "parts": [{
                "text": "Hello, respond with 'OK' if you see this."
            }]
        }]
    }
    headers = {"Content-Type": "application/json"}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=5.0)
        print(f"Model: {model} -> Status: {r.status_code}")
        if r.status_code == 200:
            print("Response:", r.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text'))
        else:
            print("Error Response:", r.text)
    except Exception as e:
        print(f"Model {model} failed: {e}")
