import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Render handles environment variables automatically!
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    payload = {
        "contents": [
            {"parts": [{"text": full_text}]}
        ]
    }

    # RECOMMENDED: v1beta is often more reliable for Flash 1.5 free keys
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    # This prints the EXACT reason for a 404 to your Render logs
    if response.status_code != 200:
        print(f"DEBUG: Google API Error ({response.status_code}): {response.text}")

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
    # Render uses port 10000 by default, this line handles that
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
