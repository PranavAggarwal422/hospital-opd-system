document.addEventListener("DOMContentLoaded", function () {
  const chatbotToggle = document.getElementById("chatbotToggle");
  const chatbotWindow = document.getElementById("chatbotWindow");
  const closeChatbot = document.getElementById("closeChatbot");
  const sendChatMessage = document.getElementById("sendChatMessage");
  const chatbotInput = document.getElementById("chatbotInput");
  const chatbotMessages = document.getElementById("chatbotMessages");

  const FASTAPI_URL = "http://127.0.0.1:8000";

  let sessionId = null;

  // OPEN CHAT
  if (chatbotToggle) {
    chatbotToggle.addEventListener("click", async () => {
      chatbotWindow.classList.add("active");

      if (!sessionId) {
        try {
          const response = await fetch(`${FASTAPI_URL}/start-chat`, {
            method: "POST",
          });

          const data = await response.json();
          sessionId = data.session_id;
        //   console.log(sessionId);
        } 
        
        catch (error) {
          console.error(error);
        }
      }
    });
  }

  // CLOSE CHAT
  if (closeChatbot) {
    closeChatbot.addEventListener("click", () => {
      chatbotWindow.classList.remove("active");
    });
  }

  // SEND MESSAGE
  async function sendMessage() {
    const message = chatbotInput.value.trim();
    if (!message || !sessionId) return;
    appendMessage(message, "user");
    chatbotInput.value = "";

    try {
      const response = await fetch(`${FASTAPI_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          prompt: message,
        }),
      });

      const data = await response.json();
      appendMessage(data.response, "bot");
    } 

    catch (error) {
      console.error(error);
      appendMessage("Sorry, AI service is unavailable right now.", "bot");
    }
  }

  // APPEND MESSAGE
  function appendMessage(message, type) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add(type === "user" ? "user-message" : "bot-message");
    messageDiv.innerHTML = message.replace(/\n/g, "<br>");

    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  // BUTTON SEND
  if (sendChatMessage) {
    sendChatMessage.addEventListener("click", sendMessage);
  }

  // ENTER SEND
  if (chatbotInput) {
    chatbotInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  }
});
