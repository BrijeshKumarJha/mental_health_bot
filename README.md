# AI-Driven Empathetic Mental Health Support Chatbot

A full-stack, responsive conversational AI web application engineered to provide immediate, empathetic mental health support. Powered by **Llama 3.3 (70B)** via the **Groq LPU API**, this application features sub-second response times and robust Natural Language Processing (NLP) safety guardrails to intercept crisis situations and offensive language.

## 🚀 Features

*   **Empathetic Conversational AI:** Utilizes the Llama 3.3 70B model, strictly prompted to act as a non-judgmental, empathetic listener that avoids medical diagnosing.
*   **Real-Time Crisis Interception:** Built-in NLP safety guardrails scan user input for high-risk crisis keywords. If detected, the system safely bypasses the AI generation layer and instantly routes the user to professional emergency resources (e.g., KIRAN Helpline).
*   **Profanity & Content Filtering:** Intercepts offensive or restricted language to maintain a safe and respectful environment.
*   **Persistent Context Memory:** Uses a JSON-based global array to track conversation history, allowing the LLM to maintain dialogue context throughout the session.
*   **Asynchronous Frontend UI:** A clean, responsive chat interface built with Vanilla JavaScript and CSS, featuring dynamic typing indicators and timestamped message logs.
*   **Local Logging System:** Automatically records session transcripts and system routing decisions into a structured `chat_logs.json` file for monitoring and analysis.

## 🛠️ Technology Stack

*   **Backend:** Python 3.10+, Flask
*   **AI Inference:** Groq API
*   **LLM Model:** `llama-3.3-70b-versatile`
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript (ES6+), Fetch API
*   **Data Serialization:** JSON

## 📂 Project Structure

```text
├── app.py                  # Main Flask server and API routing logic
├── chat_logs.json          # Auto-generated transcript and system log file
├── templates/
│   └── index.html          # Main chat interface layout
├── static/
│   ├── style.css           # UI styling and animations
│   └── script.js           # Asynchronous API fetching and DOM manipulation
└── README.md
