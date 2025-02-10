from flask import Flask, render_template, request, jsonify, session
import requests
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# API Settings
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# Flask App
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_default_secret_key")

# Load Knowledge Base (Custom Data)
def load_knowledge_base():
    if os.path.exists("knowledge_base.txt"):
        with open("knowledge_base.txt", "r", encoding="utf-8") as file:
            return file.read()
    return ""

# Search for relevant data in the knowledge base
def find_relevant_info(user_query):
    knowledge_data = load_knowledge_base().split("\n")
    relevant_info = "\n".join([line for line in knowledge_data if any(word in line.lower() for word in user_query.lower().split())])
    return relevant_info if relevant_info else "No relevant information found."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        print(f":User  {user_message}")

        # Maintain chat history
        if "chat_history" not in session:
            session["chat_history"] = []

        # Retrieve relevant information from knowledge base
        relevant_info = find_relevant_info(user_message)

        # Construct the chat prompt
        full_prompt = f"Use the following knowledge base to answer accurately:\n\n{relevant_info}\n\n:User  {user_message}\nAxis:"

        # Append user message to chat history
        session["chat_history"].append({"role": "user", "content": user_message})

        # Request payload
        payload = {
            "model": "mistralai/mistral-7b-instruct",  # You can switch models
            "messages": [{"role": "system", "content": full_prompt}] + session["chat_history"]
        }

        # Send request to OpenRouter API
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            result = response.json()
            bot_reply = result["choices"][0]["message"]["content"]

            # Append bot response to chat history
            session["chat_history"].append({"role": "assistant", "content": bot_reply})

            return jsonify({"reply": bot_reply})
        else:
            print(f"API Error: {response.text}")
            return jsonify({"reply": "Sorry, the AI is not responding. Try again later."}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"reply": "An error occurred!"}), 500

if __name__ == "__main__":
    app.run(debug=True)