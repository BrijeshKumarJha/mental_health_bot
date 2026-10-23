from flask import Flask, render_template, request, jsonify
from datetime import datetime
from groq import Groq
import os  # <-- NEW: Needed to read environment variables

# --- NEW IMPORTS ---
from flask_sqlalchemy import SQLAlchemy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dotenv import load_dotenv  # <-- NEW: Loads the .env file

# --- NEW: SECURITY LOADING ---
# This reads your .env file and secretly loads the key into the environment
load_dotenv() 

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE SCHEMA ---
class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50))
    user_message = db.Column(db.String(500))
    bot_response = db.Column(db.String(1000))
    sentiment_score = db.Column(db.Float)

# Create the database tables automatically
with app.app_context():
    db.create_all()

# --- NLTK INITIALIZATION ---
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

# --- NEW: SECURE API KEY RETRIEVAL ---
# Retrieves the key from the environment instead of hardcoding it
API_KEY = os.getenv("GROQ_API_KEY") 

if not API_KEY:
    raise ValueError("GROQ_API_KEY is missing! Make sure your .env file is set up correctly.")

client = Groq(api_key=API_KEY)
chat_history = [
    {"role": "system", "content": "You are an empathetic mental health assistant specifically designed to support students and young adults in India. You understand the unique cultural context of Indian society, including extreme academic pressure (board exams, JEE, NEET, university grades), intense family/parental expectations, and the societal stigma surrounding mental health. You are capable of understanding and responding to 'Hinglish' (Hindi written in the English alphabet). You will provide culturally sensitive support, never diagnose conditions, and keep responses conversational."}
]

restricted_words = ["idiot", "stupid", "dumb", "ugly"]
def contains_restricted_words(text):
    words = text.lower().split()
    for word in words:
        if word in restricted_words:
            return True
    return False

crisis_phrases = ["suicide", "kill", "die", "harm", "hurt", "hopeless", "give up", "end it", "end my life"]
crisis_phrases = ["suicide", "kill", "die", "harm", "hurt", "hopeless", "give up", "end it", "end my life"]

def contains_crisis_words(text):
    # 1. Strip basic punctuation so words aren't glued to commas or periods
    clean_text = text.lower().replace(".", "").replace(",", "").replace("!", "").replace("?", "")
    
    # 2. Pad the text with spaces on both sides
    padded_text = " " + clean_text + " "
    
    for phrase in crisis_phrases:
        # 3. Pad the crisis phrase with spaces on both sides
        padded_phrase = " " + phrase + " "
        
        # Now it looks for " die " instead of just "die"
        if padded_phrase in padded_text:
            return True
            
    return False

# --- DATABASE LOGGING FUNCTION ---
def log_interaction_db(user_input, bot_output, sentiment):
    new_log = ChatLog(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_message=user_input,
        bot_response=bot_output,
        sentiment_score=sentiment
    )
    db.session.add(new_log)
    db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    user_message = request.json.get("message")
    
    # --- CALCULATE SENTIMENT ---
    sentiment = sia.polarity_scores(user_message)
    compound_score = sentiment['compound']
    

    if contains_restricted_words(user_message):
            reply = "Let's keep our space respectful. I am here to help you, but I cannot process offensive language."
            log_interaction_db(user_message, reply, compound_score)
            return jsonify({"response": reply})
 # --- CRISIS INTERVENTION LOGIC ---
    if compound_score <= -0.9 or contains_crisis_words(user_message):
        reply = "It sounds like you are going through a very difficult time. Please reach out for professional help immediately. You can call the Tele-MANAS helpline at 14416 or 1800-891-4416, or contact emergency services at 112."
        log_interaction_db(user_message, reply, compound_score)
        return jsonify({"response": reply})
    
    
    try:
        chat_history.append({"role": "user", "content": user_message})
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=chat_history,
            temperature=0.7,
            max_tokens=10000
        )
        
        bot_reply = completion.choices[0].message.content
        chat_history.append({"role": "assistant", "content": bot_reply})
    except Exception as e:
        bot_reply = f"Sorry, my connection to the cloud was interrupted. Please try again."
        print(f"Error: {e}")
        if chat_history[-1]["role"] == "user":
            chat_history.pop()
    
    # Save the successful interaction to the SQL database
    log_interaction_db(user_message, bot_reply, compound_score)
    return jsonify({"response": bot_reply})

@app.route("/clear_chat", methods=["POST"])
def clear_chat():
    global chat_history
    # Reset the chat history back to only the system prompt
    chat_history = [
        {"role": "system", "content": "You are an empathetic mental health assistant here to listen, support, and help the user talk through their feelings. You will not judge, you will keep responses conversational and relatively brief, and you will never diagnose medical conditions."}
    ]
    return jsonify({"status": "success", "message": "Chat history cleared."})

if __name__ == "__main__":
    app.run(debug=True)