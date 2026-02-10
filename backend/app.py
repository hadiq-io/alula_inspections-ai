# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_service import AIService
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize AI Service
ai_service = AIService()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get AI response
        response = ai_service.chat(user_message)
        
        return jsonify(response), 200
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear conversation history"""
    try:
        ai_service.clear_history()
        return jsonify({"success": True, "message": "Chat cleared"}), 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "healthy", "service": "AlUla AI Backend"}), 200

if __name__ == '__main__':
    print("🚀 Starting AlUla AI Backend...")
    print("📍 Listening on http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
