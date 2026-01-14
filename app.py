import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    payload = { "contents":[{"parts":[{"text": full_text}]}] }
    
    # This is the most standard URL for the Flash model
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    res = requests.post(
        url,
        params={"key": GEMINI_API_KEY}, # Moving the key to a parameter can sometimes fix 404s
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if res.status_code != 200:
        print(f"DEBUG: Google API Error: {res.text}") # This shows the REAL error in Render logs
    
    res.raise_for_status()
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.json or {}
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({'reply': "Please enter a message."})
    
    try:
        reply = ask_gemini(user_input)
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return jsonify({'reply': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
