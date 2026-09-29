import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.6-flash"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in the .env file.")

client = genai.Client(api_key=API_KEY)

with open("chatbot_config.txt", "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read().strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a question about toys."}), 400

    try:
        prompt = f"""{SYSTEM_PROMPT}

User question:
{user_message}

Answer the user according to the chatbot rules above.
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        reply = getattr(response, "text", None)
        if not reply:
            reply = "I couldn't generate a response right now. Please try again."

        return jsonify({"reply": reply.strip()})

    except Exception as error:
        print(f"Gemini API error: {error}")
        return jsonify({
            "reply": "Sorry, I couldn't connect to the AI service right now. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
