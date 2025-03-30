from flask import Flask, render_template, request, jsonify

import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="ur key")
model = genai.GenerativeModel("gemini-1.5-flash")

chat_history = []  # Temporary storage (clears when server restarts)

def chat_with_gemini(user_code):
    prompt = f"Tell:\n\n{user_code}"
    response = model.generate_content(prompt)
    return response.text if response else "Sorry, I couldn't analyze this code."

# def chatbot_response(user_message):
#     responses = {
#         "hello": "Hi there! 😊 How can I help you?",
#         "how are you": "I'm just a bot, but I'm doing great! What about you?",
#         "bye": "Goodbye! Have a great day! 👋",
#     }
#     return responses.get(user_message.lower(), "I'm not sure about that 🤔, but I'm always learning!")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    # bot_reply = chatbot_response(user_message)

    bot_response = chat_with_gemini(user_message)

    chat_history.append({"user": user_message, "bot": bot_response})  # Store chat in list

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
