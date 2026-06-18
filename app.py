from flask import Flask, render_template, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import os
from datetime import datetime

app = Flask(__name__)

print("Waking up AI...")
model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
print("AI is awake and ready!")

chat_history_ids = None

persona_setup = "User: Hello. Who are you?\nBot: I am an empathetic mental health assistant here to listen, support, and help you talk through your feelings. I will not judge you.\nUser: "
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
    global chat_history_ids

    user_message = request.json.get("message")
    
    if contains_crisis_words(user_message):
        reply = "It sounds like you are going through a very difficult time. Please reach out for professional help immediately. You can call the KIRAN helpline at 1800-599-0019 or contact emergency services at 112."
        log_interaction(user_message, reply)
        return jsonify({"response": reply})

    if contains_restricted_words(user_message):
        reply = "Let's keep our space respectful. I am here to help you, but I cannot process offensive language."
        log_interaction(user_message, reply)
        return jsonify({"response": reply})

    if chat_history_ids is None:
        hidden_prompt = persona_setup + user_message
        new_user_input_ids = tokenizer.encode(hidden_prompt + tokenizer.eos_token, return_tensors='pt')
        bot_input_ids = new_user_input_ids
    else:
        new_user_input_ids = tokenizer.encode(user_message + tokenizer.eos_token, return_tensors='pt')
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1)
    
    chat_history_ids = model.generate(
        bot_input_ids, 
        max_length=1000, 
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=3,
        do_sample=True,
        temperature=0.7,
        top_k=50,
        top_p=0.9
    )
    bot_reply = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    log_interaction(user_message, bot_reply)
    return jsonify({"response": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
