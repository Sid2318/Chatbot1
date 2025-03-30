from flask import Flask, render_template, request, jsonify
from markdown2 import markdown  # Add this import
import uuid  # For session handling
import google.generativeai as genai

app = Flask(__name__)

genai.configure(api_key="AIzaSyD3IHgDTHiHU3QffVML_P2qBXkQN8Zd-mY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Add this constant
SYSTEM_PROMPT = """You are CodeHelper, an AI assistant specializing in programming. Always format responses with:
1. **Headings** for main sections
2. Bullet points for lists
3. Code blocks with language specification
4. Bold for important terms
5. Clear separation between sections"""

chat_history = []  # Temporary storage (clears when server restarts)

def chat_with_gemini(user_input):
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nUser Query: {user_input}"
        response = model.generate_content(
            prompt,
            # generation_config={
            #     "max_output_tokens": 2048,
            #     "temperature": 0.5,   
            #     "top_p": 0.95
            # }
        )
        return response.text if response else "Sorry, I couldn't process that request."
    except Exception as e:
        return f"An error occurred: {str(e)}"

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
    html_response = markdown(bot_response, extras=["fenced-code-blocks", "tables"])
    
    chat_history.append({"user": user_message, "bot": html_response})
    return jsonify({"response": html_response})

if __name__ == "__main__":
    app.run(debug=True)
