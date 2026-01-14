import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Render picks this up from your Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(full_text):
    payload = { "contents":[{"parts":[{"text": full_text}]}] }
    
    # FIXED URL: Changed 'v1beta' to 'v1' to avoid 404
    api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    
    res = requests.post(
        api_url,
        headers={"Content-Type": "application/json", "X-goog-api-key": GEMINI_API_KEY},
        json=payload
    )
    
    # This will now give a clear error in Render logs if the API key is wrong
    res.raise_for_status()
    
    data = res.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.json or {}
    user_input = data.get('message', '').strip()
    
    if not user_input:
        return jsonify({'reply': "Please enter a message."})
    
    # System prompt to give the AI some personality
    full_text = f"You are a helpful assistant for ARED. User says: {user_input}"
    
    try:
        reply = ask_gemini(full_text)
        return jsonify({'reply': reply})
    except Exception as e:
        # This helps us debug in the Render logs
        print(f"Error occurred: {str(e)}")
        return jsonify({'reply': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
