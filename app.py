import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    payload = {
        "contents": [
            {"parts": [{"text": full_text}]}
        ]
    }

    # CHANGE: Switched to gemini-2.0-flash-exp (Experimental/New)
    # This often bypasses the 404 'Not Found' error on newer accounts
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"DEBUG: Google API Error ({response.status_code}): {response.text}")
        
        # SECOND ATTEMPT: If 2.0 fails, try the absolute basic version
        if response.status_code == 404:
            print("Retrying with gemini-pro...")
            url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
            response = requests.post(url_fallback, headers=headers, json=payload)

    response.raise_for_status()
    data = response.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]

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
