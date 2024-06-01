const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const chatHistory = document.getElementById('chat-history');

sendButton.addEventListener('click', async () => {
    const message = userInput.value.trim();
    if (message) {
      appendMessage('user', message);
      userInput.value = '';
  
      const formData = new FormData();
      formData.append('message', message); // Add user message as form data
  
      const response = await fetch('http://localhost:8000/chatbot', {
        method: 'POST', // Use POST method for form data
        body: formData
      })
        .then(res => res.json());
      appendMessage('bot', response.message);
    }
  });

  function appendMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerText = message;
    if (sender === 'bot') {
      messageElement.classList.add('bot-message');
    } else {
      messageElement.classList.add('user-message');
    }
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight; // Scroll to the bottom
  }
