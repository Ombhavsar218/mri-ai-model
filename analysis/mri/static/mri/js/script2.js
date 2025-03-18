document.addEventListener("DOMContentLoaded", function () {
    // Automatically remove popup after a delay (e.g., 10 seconds)
    const popupOverlay = document.querySelector(".popup-overlay");
    const popupModal = document.querySelector(".popup-modal");

    if (popupOverlay && popupModal) {
        setTimeout(() => {
            popupOverlay.remove();
            popupModal.remove();
        }, 10000); // 10 seconds
    }

    // Toggle password visibility
    const togglePasswordIcons = document.querySelectorAll(".toggle-password");
    togglePasswordIcons.forEach(icon => {
        icon.addEventListener("click", function () {
            const input = document.querySelector(this.getAttribute("toggle"));
            if (input) {
                if (input.type === "password") {
                    input.type = "text";
                    this.classList.remove("fa-eye");
                    this.classList.add("fa-eye-slash");
                } else {
                    input.type = "password";
                    this.classList.remove("fa-eye-slash");
                    this.classList.add("fa-eye");
                }
            } else {
                console.error("Input element not found for toggle selector:", this.getAttribute("toggle"));
            }
        });
    });

    // Close popup on button click
    const closePopupButtons = document.querySelectorAll(".popup-modal button");
    closePopupButtons.forEach(button => {
        button.addEventListener("click", function () {
            const popupOverlay = document.querySelector(".popup-overlay");
            const popupModal = document.querySelector(".popup-modal");
            if (popupOverlay && popupModal) {
                popupOverlay.remove();
                popupModal.remove();
            }
        });
    });

    // Chat Modal Functionality
    const chatButton = document.getElementById("chatButton");
    const chatModal = document.getElementById("chatModal");
    const closeChat = document.getElementById("closeChat");
    const sendMessageButton = document.getElementById("sendMessageButton");
    const userMessageInput = document.getElementById("userMessage");
    const messagesDiv = document.getElementById("messages");

    // Open chat modal and send automatic greeting message
    chatButton?.addEventListener("click", () => {
        if (chatModal.style.display === "block") {
            chatModal.style.display = "none"; // Close modal if open
        } else {
            chatModal.style.display = "block"; // Open modal if closed
            sendBotGreeting(); // Send greeting message
        }
    });

    // Close chat modal
    closeChat?.addEventListener("click", () => {
        chatModal.style.display = "none";
    });

    // Send message functionality
    function sendMessage() {
        const userMessage = userMessageInput.value.trim();
        if (userMessage !== "") {
            // Display user message
            const userMessageElement = document.createElement("div");
            userMessageElement.classList.add("message", "user-message");
            userMessageElement.textContent = userMessage;
            messagesDiv.appendChild(userMessageElement);
    
            // Log the message that will be sent
            console.log("Sending message to backend:", userMessage);
    
            // Send the user message to the backend for GPT-2 response
            fetch("/generate-response", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: userMessage })
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response from backend:", data); // Log the response
                if (data.response) {
                    // Display bot message
                    const botMessageElement = document.createElement("div");
                    botMessageElement.classList.add("message", "bot-message");
                    botMessageElement.textContent = data.response;
                    messagesDiv.appendChild(botMessageElement);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to bottom
                } else {
                    console.error("Invalid response from server", data); // Log any issues with the response
                }
            })
            .catch(error => {
                console.error("Error sending message:", error); // Log any errors during the fetch
            });
    
            // Clear the input field
            userMessageInput.value = "";
        }
    }
    

    sendMessageButton?.addEventListener("click", sendMessage);

    // Send message functionality when pressing Enter
    userMessageInput?.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevents the default behavior (like creating a new line)
            sendMessage(); // Call the send message function
        }
    });

    // Close chat modal when clicking outside
    window.addEventListener("click", (event) => {
        if (event.target === chatModal) {
            chatModal.style.display = "none";
        }
    });

    // Function to send a bot message
    function sendBotMessage(message) {
        const botMessageElement = document.createElement("div");
        botMessageElement.classList.add("message", "bot-message");
        botMessageElement.textContent = message;
        messagesDiv.appendChild(botMessageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to the bottom
    }

    // Function to send a bot greeting message
    function sendBotGreeting() {
        sendBotMessage("Hello! 👋 Welcome to MEDAI.\n How can I help you today?"); // Greeting message
    }
});
