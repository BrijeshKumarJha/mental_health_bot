const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');

function sendMessage(){
    const text = userInput.value.trim();
    if(text === "") return;

    appendMessage(text, 'user-message');
    userInput.value = '';

    typingIndicator.classList.remove('hidden');
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ message: text})
    })
    .then(response => response.json())
    .then(data => {
        typingIndicator.classList.add('hidden');
        appendMessage(data.response, 'bot-message');
    })
    .catch(error => {
        typingIndicator.classList.add('hidden');
        console.error("Error connecting to server:", error);
        
    });
}

function appendMessage(text, className) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + className;
    msgDiv.textContent = text;

    const timeSpan = document.createElement('span');
    timeSpan.className = 'timestamp';
    const now = new Date();
    timeSpan.textContent = now.toLocaleTimeString([], {hour:'2-digit', minute: '2-digit'});
    msgDiv.appendChild(timeSpan);
    chatBox.appendChild(msgDiv);
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', function(e) {
    if(e.key === 'Enter') sendMessage();
});

document.addEventListener("DOMContentLoaded", function() {
    const quickExitBtn = document.getElementById("quick-exit-btn");

    function executeQuickExit() {
        // 1. Tell the Flask backend to erase the server-side chat history
        fetch("/clear_chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        }).then(() => {
            // 2. Clear any messages currently displayed on the screen
            const chatBox = document.getElementById("chat-box"); // Ensure this matches your chat container ID
            if(chatBox) chatBox.innerHTML = "";
            
            // 3. Instantly redirect to a safe, neutral website
            window.location.replace("https://www.google.com/webhp");
        }).catch(err => {
            // Even if the server fails, prioritize user safety and redirect immediately
            window.location.replace("https://www.google.com/webhp");
        });
    }

    // Trigger exit on button click
    if (quickExitBtn) {
        quickExitBtn.addEventListener("click", executeQuickExit);
    }

    // Trigger exit if the user presses the 'Escape' key twice rapidly (Standard accessibility practice)
    let escCount = 0;
    let escTimer;
    document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            escCount++;
            if (escCount === 2) {
                executeQuickExit();
            }
            clearTimeout(escTimer);
            escTimer = setTimeout(() => { escCount = 0; }, 1000); // Reset count after 1 second
        }
    });
});