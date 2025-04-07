from flask import Flask, render_template, request, jsonify, session
from markdown2 import markdown  # Markdown support for better formatting
import uuid  # For session handling
import os
import google.generativeai as genai
from googleapiclient.discovery import build  # YouTube API
# from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "c674707ef5d2e8be9b66e06e200d4946c4aa61541b0b2d1052c69a01a809b334"  # Required for session handling

# Configure Gemini AI
genai.configure(api_key="your_api_key")
model = genai.GenerativeModel("gemini-1.5-flash", #generation_config={
    # "max_output_tokens": 2048,
    # "temperature": 0.5,
    # "top_p": 0.95
#}
)
# YouTube API Configuration
YOUTUBE_API_KEY = "AIzaSyBBvAoqs0h5ZmtPSbUmzXEIG_GF1yzclLU"
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
# const API_KEY = "AIzaSyBBvAoqs0h5ZmtPSbUmzXEIG_GF1yzclLU";

# System role prompt for the chatbot
SYSTEM_PROMPT = """**Role**: You're CodeMentor, an AI programming assistant that automatically adapts to user needs.  
🚫 **Restriction**: Only respond to topics related to programming, coding, and technology. Ignore any unrelated queries.  

1️⃣ **For Code Submissions** 💻:  
   - Detect the programming language.  
   - Analyze for: 🐛 Bugs (with line numbers), ⚡ Performance issues, 🔒 Security vulnerabilities, 📝 Style improvements.  
   - For DSA problems: Provide time/space complexity analysis, optimized solutions, and comparisons.  
   - Always include: Complete corrected code, line-by-line explanations, before/after comparisons.  

   - **Comparison Table for Optimization**:  

     | Aspect               | Original Code | Optimized Code |
     |----------------------|--------------|---------------|
     | **Logic Improvement**| Explain original logic | Explain optimized approach |
     | **Time Complexity**  | O(original)  | O(optimized) |
     | **Space Complexity** | O(original)  | O(optimized) |
     | **Key Changes**      | List major inefficiencies | List improvements |

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

   - **Guided Learning**:  
     - If mistakes are found, suggest **3-5 thought-provoking questions** to help users identify and understand their errors.
     - The questions should be in **link format** from valid external websites.
     - Each link should be named after the **problem title** from that website.
     - Questions should be presented as a **bullet list**.
     - **All links should be valid and functional.**

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
        
         # **Extract Main Issue**
        main_issue = extract_main_issue(bot_reply)

        # Store conversation history (Limited to last 10 exchanges)
        chat_history.append(f"User: {user_input}\nBot: {bot_reply}")
        chat_sessions[session_id] = chat_history[-10:]

        return bot_reply, main_issue
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"

def extract_main_issue(bot_reply):
    """Asks Gemini AI to extract major logic issues from the bot's response."""
    try:
        # Explicitly instruct Gemini to identify the logic issue
        issue_prompt = f"""
        Analyze the following chatbot response and extract the **primary logic issues**.
        Only return the **specific problem(s)** without extra text.

        Response:
        {bot_reply}

        Expected Output:
        - List major logic issues (e.g., "Infinite loop", "Incorrect condition check", "Off-by-one error").
        """

        # Call Gemini AI to extract logical issues
        response = model.generate_content(issue_prompt)
        extracted_issues = response.text.strip() if response else "No critical issue detected."

        return extracted_issues
    except Exception as e:
        return f"⚠️ Error extracting issue: {str(e)}"

def search_youtube(query):
    """Search YouTube for relevant videos based on the detected issue."""
    try:
        request = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=3,
            type="video"
        )
        response = request.execute()

        videos = [
            {
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            }
            for item in response.get("items", [])
        ]

        return videos
    except Exception as e:
        return [{"title": "Error fetching videos", "url": "#"}]

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
    bot_response, main_issue = chat_with_gemini(user_message, session_id)

    html_response = markdown(bot_response, extras=["fenced-code-blocks", "tables"])
    
    youtube_videos = []
    if main_issue != "No critical issue detected.":
        youtube_videos = search_youtube(main_issue)
    
    # **Format YouTube Videos in the Response**
    if youtube_videos:
        video_section = "<br><br><strong>🎥 For better understanding, refer to these videos:</strong><ul>"
        for video in youtube_videos:
            video_section += f'<li><a href="{video["url"]}" target="_blank">{video["title"]}</a></li>'
        video_section += "</ul>"
        html_response += video_section  # Append to chatbot response

    
    return jsonify({
        "response": html_response
    })

if __name__ == "__main__":
    app.run(debug=True)
