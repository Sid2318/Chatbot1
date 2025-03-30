function sendMessage() {
    let inputField = document.getElementById("userInput");
    let userMessage = inputField.value.trim();
    if (userMessage === "") return;

    // Display user message
    displayMessage(userMessage, "user");

    // Send message to Flask backend
    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.response, "bot");
    });

    inputField.value = ""; // Clear input field
}
function displayMessage(message, sender, isMarkdown = false) {
    let chatbox = document.getElementById("chatbox");
    let messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);
    
    if (sender === "bot") {
        // For bot messages, render the HTML directly
        messageElement.innerHTML = message;
    } else {
        // For user messages, keep as plain text
        messageElement.textContent = message;
    }
    
    chatbox.appendChild(messageElement);
    chatbox.scrollTop = chatbox.scrollHeight;
}

// function displayMessage(message, sender) {
//     let chatbox = document.getElementById("chatbox");
//     let messageElement = document.createElement("div");
//     messageElement.classList.add("message", sender);
//     messageElement.textContent = message;
//     chatbox.appendChild(messageElement);
//     chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll
// }

document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    
    // Check for saved theme preference or use preferred color scheme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Set initial theme
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark-theme');
    }
    
    // Toggle theme on button click
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
});