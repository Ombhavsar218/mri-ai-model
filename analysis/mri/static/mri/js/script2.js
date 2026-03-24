document.addEventListener("DOMContentLoaded", function () {
    // ===========================
    // Auto-remove popup after 10s
    // ===========================
    const popupOverlay = document.querySelector(".popup-overlay");
    const popupModal = document.querySelector(".popup-modal");

    if (popupOverlay && popupModal) {
        setTimeout(() => {
            popupOverlay.remove();
            popupModal.remove();
        }, 10000); // 10 seconds
    }

    // ===========================
    // Toggle password visibility
    // ===========================
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

    // ===========================
    // Close popup on button click
    // ===========================
    const closePopupButtons = document.querySelectorAll(".popup-modal button");
    closePopupButtons.forEach(button => {
        button.addEventListener("click", function () {
            if (popupOverlay && popupModal) {
                popupOverlay.remove();
                popupModal.remove();
            }
        });
    });

    // ===========================
    // Toggle between Doctor and Expert Doctor forms (Sliding Effect)
    // ===========================
    const doctorTab = document.getElementById("doctor-tab");
    const expertTab = document.getElementById("expert-tab");
    const doctorLogin = document.getElementById("doctor-login");
    const expertLogin = document.getElementById("expert-login");

    if (doctorTab && expertTab && doctorLogin && expertLogin) {
        doctorTab.addEventListener("click", function () {
            doctorLogin.style.display = "block";
            expertLogin.style.display = "none";
            doctorTab.classList.add("active-tab");
            expertTab.classList.remove("active-tab");
        });

        expertTab.addEventListener("click", function () {
            doctorLogin.style.display = "none";
            expertLogin.style.display = "block";
            expertTab.classList.add("active-tab");
            doctorTab.classList.remove("active-tab");
        });
    }

    // ===========================
    // Chat Modal Functionality
    // ===========================
    const chatButton = document.getElementById("chatButton");
    const chatModal = document.getElementById("chatModal");
    const closeChat = document.getElementById("closeChat");
    const sendMessageButton = document.getElementById("sendMessageButton");
    const userMessageInput = document.getElementById("userMessage");
    const messagesDiv = document.getElementById("messages");

    const botResponses = {
        "what is a brain tumor": "A brain tumor is a mass of abnormal cells in your brain. It can be benign or malignant.",
        "how does mri detect tumors": "MRI uses magnetic fields to capture detailed images of the brain, helping detect abnormalities like tumors.",
        "how accurate is the ai model": "Our AI model is trained using YOLOv8 and achieves around 95% detection accuracy on validated datasets.",
        "how to upload mri": "You can upload an MRI via the 'Upload' button on the dashboard.",
        "how to download report": "Go to your MRI result and click on the download icon to save your report.",
        "show me patients with tumor detected": "Visit the 'Patients' section and use the tumor filter to see only those cases.",
        "tell me a joke": "Why did the neuron break up with the synapse? Too much pressure!",
        "who built you": "I was built by a team of developers and AI experts to assist with medical insights!",
    };

    function normalizeText(text) {
        return text.toLowerCase().replace(/[^\w\s]/gi, '');
    }

    // Open chat modal and send greeting
    chatButton?.addEventListener("click", () => {
        if (chatModal.style.display === "block") {
            chatModal.style.display = "none";
        } else {
            chatModal.style.display = "block";
            sendBotGreeting();
        }
    });

    closeChat?.addEventListener("click", () => {
        chatModal.style.display = "none";
    });

    // Function to send a bot message
    function sendBotMessage(message) {
        const botMessageElement = document.createElement("div");
        botMessageElement.classList.add("message", "bot-message");
        botMessageElement.textContent = message;
        messagesDiv.appendChild(botMessageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // Greeting on open
    function sendBotGreeting() {
        sendBotMessage("Hello! 👋 Welcome to MEDAI.\nHow can I help you today?");
    }

    // Send message logic
    function sendMessage() {
        const userMessage = userMessageInput.value.trim();
        if (userMessage === "") return;

        // Display user message
        const userMessageElement = document.createElement("div");
        userMessageElement.classList.add("message", "user-message");
        userMessageElement.textContent = userMessage;
        messagesDiv.appendChild(userMessageElement);

        // Call backend
        fetch("/generate-response", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response && data.response.trim() !== "") {
                sendBotMessage(data.response);
            } else {
                fallbackResponse(userMessage);
            }
        })
        .catch(() => {
            fallbackResponse(userMessage);
        });

        userMessageInput.value = "";
    }

    // Local fallback if no response from backend
    function fallbackResponse(userInput) {
        const normalized = normalizeText(userInput);
        const reply = botResponses[normalized] || "Sorry, I didn't understand that. Try asking about MRI, tumors, uploading reports, or AI model.";
        sendBotMessage(reply);
    }

    sendMessageButton?.addEventListener("click", sendMessage);
    userMessageInput?.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    window.addEventListener("click", (event) => {
        if (event.target === chatModal) {
            chatModal.style.display = "none";
        }
    });
});
