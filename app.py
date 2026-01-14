import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    payload = { "contents":[{"parts":[{"text": full_text}]}] }
    res = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        headers={"Content-Type":"application/json","X-goog-api-key":GEMINI_API_KEY},
        json=payload
    )
    res.raise_for_status()
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.json or {}
    user_input = data.get('message','').strip()
    if not user_input:
        return jsonify({'reply':"Please enter a message."})
    
    # Simple prompt for now to test
    full_text = "You are a helpful assistant. User says: " + user_input
    try:
        reply = ask_gemini(full_text)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    # This part is crucial for Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
