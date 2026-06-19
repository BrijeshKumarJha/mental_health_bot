from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from groq import Groq

app = Flask(__name__)

API_KEY = "Paste your Api Key here"
client = Groq(api_key=API_KEY)
# chat_session = None
chat_history = [
    {"role": "system", "content": "You are an empathetic mental health assistant here to listen, support, and help the user talk through their feelings. You will not judge, you will keep responses conversational and relatively brief, and you will never diagnose medical conditions."}
]

restricted_words = ["idiot", "stupid", "hate", "dumb", "ugly"]
def contains_restricted_words(text):
    words = text.lower().split()
    for word in words:
        if word in restricted_words:
            return True
    return False

crisis_words = ["suicide", "kill", "die", "harm", "hurt"]
def contains_crisis_words(text):
    words = text.lower().split()
    for word in words:
        if word in crisis_words:
            return True
    return False

def log_interaction(user_input, bot_output):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_message": user_input,
        "bot_response": bot_output
    }
    if os.path.exists("chat_logs.json"):
        with open("chat_logs.json", "r") as file:
            try:
                logs = json.load(file)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []
    
    logs.append(log_entry)
    with open("chat_logs.json", "w") as file:
        json.dump(logs, file, indent=4)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_message = request.json.get("message")
    
    if contains_crisis_words(user_message):
        reply = "It sounds like you are going through a very difficult time. Please reach out for professional help immediately. You can call the KIRAN helpline at 1800-599-0019 or contact emergency services at 112."
        log_interaction(user_message, reply)
        return jsonify({"response": reply})
    
    if contains_restricted_words(user_message):
        reply = "Let's keep our space respectful. I am here to help you, but I cannot process offensive language."
        log_interaction(user_message, reply)
        return jsonify({"response": reply})
    
    try:
        chat_history.append({"role": "user", "content": user_message})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_history,
            temperature=0.7,
            max_tokens=12000
        )
        
        bot_reply = completion.choices[0].message.content
        chat_history.append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        bot_reply = f"Sorry, my connection to the cloud was interrupted. Please try again."
        print(f"Error: {e}")
        if chat_history[-1]["role"] == "user":
            chat_history.pop()
    
    
    log_interaction(user_message, bot_reply)
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
