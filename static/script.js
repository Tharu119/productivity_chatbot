const socket = io({ transports: ['websocket', 'polling', 'flashsocket'] });

async function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    let chatBox = document.getElementById("chat-box");

    if (userInput.trim() === "") return;

    // Add user message to chat box
    let userMessage = `<p class="user-message"><strong>You:</strong> ${userInput}</p>`;
    chatBox.innerHTML += userMessage;
    document.getElementById("user-input").value = "";

    let endpoint = "/chat";
    if (userInput.toLowerCase().includes("remind me")) {
        endpoint = "/add_reminder";
    } else if (userInput.toLowerCase().includes("list reminders")) {
        endpoint = "/list_reminders";
    } else if (userInput.toLowerCase().includes("delete reminder")) {
        endpoint = "/delete_reminder";
    }

    let response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    });

    let data = await response.json();
    let botMessage = `<p class="bot-message"><strong>Bot:</strong> ${data.response}</p>`;
    
    chatBox.innerHTML += botMessage;
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Listen for real-time reminder notifications
socket.on("reminder_notification", (data) => {
    console.log("📩 Received Notification from Server:", data.message);
    showNotification(data.message);

    // Add the reminder as a bot message in the chat
    let chatBox = document.getElementById("chat-box");
    let botMessage = `<p class="bot-message"><strong>Reminder:</strong> ${data.message}</p>`;
    chatBox.innerHTML += botMessage;
    chatBox.scrollTop = chatBox.scrollHeight;
});

// Function to show notification pop-up
function showNotification(message) {
    let notification = document.getElementById("notification");
    notification.innerText = message;
    notification.style.display = "block";  // Ensure it's visible

    setTimeout(() => {
        notification.style.display = "none";
    }, 5000);
}
