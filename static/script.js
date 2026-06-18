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

