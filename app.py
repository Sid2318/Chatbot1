from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai

# Configure Flask App
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db = SQLAlchemy(app)


genai.configure(api_key="key")
model = genai.GenerativeModel("gemini-2.0-flash")

# Database Model for Chat History
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)



# Chatbot Function
def chat_with_gemini(user_input):
    response = model.generate_content(user_input)
    return response.text

# Flask Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    bot_response = chat_with_gemini(user_input)

    # Save conversation to database
    new_chat = ChatHistory(user_message=user_input, bot_response=bot_response)
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
