from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)
load_dotenv()

# ✅ Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ✅ Initialize Gemini model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json()
#         user_message = data.get("message", "")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        # Generate response from Gemini
        response = model.generate_content(user_message)
        reply = response.text.strip() if response.text else "No response from Gemini."

        print("🧍 User:", user_message)
        print("🤖 Bot:", reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


# ✅ ADD THIS BELOW — route to list available Gemini models
@app.route("/models", methods=["GET"])
def list_models():
    models = [m.name for m in genai.list_models()]
    return jsonify(models)


if __name__ == "__main__":
    app.run(debug=True)
