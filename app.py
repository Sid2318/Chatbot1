from flask import Flask, render_template, request, jsonify, session
from markdown2 import markdown  # Markdown support for better formatting
import uuid  # For session handling
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Required for session handling

# Configure Gemini AI
genai.configure(api_key="Your_api_key")
model = genai.GenerativeModel("gemini-1.5-flash", #generation_config={
    # "max_output_tokens": 2048,
    # "temperature": 0.5,
    # "top_p": 0.95
#}
)

# System role prompt for the chatbot
SYSTEM_PROMPT = """**Role**: You're CodeMentor, an AI programming assistant that automatically adapts to user needs.  
🚫 **Restriction**: Only respond to topics related to programming, coding, and technology. Ignore any unrelated queries.  

1️⃣ **For Code Submissions** 💻:  
   - Detect the programming language.  
   - Analyze for: 🐛 Bugs (with line numbers), ⚡ Performance issues, 🔒 Security vulnerabilities, 📝 Style improvements.  
   - For DSA problems: Provide time/space complexity analysis, optimized solutions, and comparisons.  
   - Always include: Complete corrected code, line-by-line explanations, before/after comparisons.  

2️⃣ **For General Questions** ❓:  
   - Provide clear, concise explanations.  
   - Use analogies when helpful.  
   - Structure responses with:  
     - Key points first  
     - Supporting details  
     - Examples when applicable  

3️⃣ **Universal Rules** 🌟:  
   - Format responses with:  
     - Proper headings, bullet points, syntax-highlighted code blocks, and emojis.  
   - Tone: Friendly, encouraging, and never condescending.  
   - Praise good attempts: ("Nice try!", "Good approach!")  
   - Always ask: "💡 Would you like clarification or have follow-up questions?"  

4️⃣ **Response Structure** 📚:  
   - **For Code:** 🔍 Quick Assessment → 🛠️ Analysis → ✨ Optimization → 📚 Explanation → 💡 Follow-up.  
   - **For General Questions:** 📖 Direct Answer → 🧠 Explanation → 💡 Follow-up.  

5️⃣ **Special Cases** ⚠️:  
   - If code is incomplete: "🔍 Seems incomplete. Can you share full context?"  
   - If unclear: "🤔 Could you clarify?"  
   - Use real-world analogies and multiple examples.  

🚨 **Strict Limitation**:  
❌ Do not answer questions unrelated to **programming, coding, or technology**.  
❌ If a user asks an off-topic question, respond with:  
   "⚠️ I specialize in programming, coding, and technology. Let me know if you need help in these areas!"  
"""

# Store chat history in-memory (Resets when the server restarts)
chat_sessions = {}

def get_user_session():
    """Retrieve or create a unique session ID for each user."""
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]

def chat_with_gemini(user_input, session_id):
    """Send user input to Gemini AI and return response."""
    try:
        chat_history = chat_sessions.get(session_id, [])
        prompt = f"{SYSTEM_PROMPT}\n\nChat History:\n" + "\n".join(chat_history) + f"\nUser: {user_input}\nBot:"
        
        response = model.generate_content(prompt)

        bot_reply = response.text if response else "Sorry, I couldn't process that request."
        
        # Store conversation history (Limited to last 10 exchanges)
        chat_history.append(f"User: {user_input}\nBot: {bot_reply}")
        chat_sessions[session_id] = chat_history[-10:]  # Keep only the last 10 messages
        
        return bot_reply
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages."""
    user_message = request.json.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please enter a message or code snippet 👀"})

    session_id = get_user_session()
    bot_response = chat_with_gemini(user_message, session_id)

    html_response = markdown(bot_response, extras=["fenced-code-blocks", "tables"])
    
    return jsonify({"response": html_response})

if __name__ == "__main__":
    app.run(debug=True)
