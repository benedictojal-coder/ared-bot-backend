import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Render handles this automatically from your Environment Variables tab
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    """
    Tries multiple Gemini model endpoints in order of preference (2026 update).
    """
    payload = {
        "contents": [
            {"parts": [{"text": full_text}]}
        ]
    }
    headers = {"Content-Type": "application/json"}

    # 2026 Model List: Trying Gemini 3, then 2.5, then 2.0
    models_to_try = [
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent",
        "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
    ]

    last_error_msg = ""

    for url in models_to_try:
        try:
            # We append the key to the URL as a parameter
            full_url = f"{url}?key={GEMINI_API_KEY}"
            response = requests.post(full_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Return the text from the first valid candidate
                return data["candidates"][0]["content"]["parts"][0]["text"]
            
            # If not 200, log the error and try the next model in the list
            error_detail = response.json().get('error', {}).get('message', 'Unknown Error')
            print(f"DEBUG: Model {url.split('/')[-1]} failed: {error_detail}")
            last_error_msg = f"Model {url.split('/')[-1]} returned {response.status_code}: {error_detail}"
            
        except Exception as e:
            print(f"DEBUG: Connection to {url} failed: {str(e)}")
            last_error_msg = str(e)
            continue

    # If the loop finishes without returning, everything failed
    raise Exception(f"All model endpoints failed. {last_error_msg}")

@app.route("/chat", methods=["POST"])
def chatbot():
    data = request.json or {}
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "I'm listening! Please type something."})

    try:
        reply = ask_gemini(user_input)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        # If the key is still the old one, the error logs will show it here
        return jsonify({"reply": f"System Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Render binds to port 10000 by default
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
