import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    payload = { "contents": [{"parts": [{"text": full_text}]}] }
    headers = { "Content-Type": "application/json" }
    
    # We will try three different "doors" until one opens
    models_to_try = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    ]

    last_error = ""
    for url in models_to_try:
        try:
            print(f"DEBUG: Trying model URL: {url}")
            res = requests.post(f"{url}?key={GEMINI_API_KEY}", headers=headers, json=payload)
            
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            
            last_error = f"Status {res.status_code}: {res.text}"
            print(f"DEBUG: Failed {url} with {last_error}")
            
        except Exception as e:
            last_error = str(e)
            continue

    raise Exception(f"All models failed. Last error: {last_error}")

@app.route("/chat", methods=["POST"])
def chatbot():
    data = request.json or {}
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"reply": "Please enter a message."})

    try:
        reply = ask_gemini(user_input)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
