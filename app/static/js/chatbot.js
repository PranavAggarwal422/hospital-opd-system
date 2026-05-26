document.addEventListener("DOMContentLoaded", function () {
  const chatbotToggle = document.getElementById("chatbotToggle");
  const chatbotWindow = document.getElementById("chatbotWindow");
  const closeChatbot = document.getElementById("closeChatbot");
  const sendChatMessage = document.getElementById("sendChatMessage");
  const chatbotInput = document.getElementById("chatbotInput");
  const chatbotMessages = document.getElementById("chatbotMessages");
  const uploadReportBtn = document.getElementById("uploadReportBtn");
  const reportFileInput = document.getElementById("reportFileInput");

  const FASTAPI_URL = "http://127.0.0.1:8000";

  let sessionId = null;

  // OPEN CHAT
  if (chatbotToggle) {
    chatbotToggle.addEventListener("click", async () => {
      chatbotWindow.classList.add("active");
      chatbotToggle.style.display = "none";

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
      chatbotToggle.style.display = "flex";
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
    messageDiv.innerHTML = marked.parse(message);

    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  // OPEN FILE PICKER
  if(uploadReportBtn) {
    uploadReportBtn.addEventListener("click", () => {
      reportFileInput.click();
    });
  }

  // HANDLE REPORT UPLOAD
  if(reportFileInput) {
    reportFileInput.addEventListener("change", async function (e) {
      const file = e.target.files[0];
      if (!file || !sessionId) return;

      appendMessage(`Uploaded Report: ${file.name}`, "user");
      appendMessage("Analyzing medical report...", "bot");

      try {
        const formData = new FormData();

        formData.append("session_id", sessionId);
        formData.append("file", file);

        const response = await fetch(`${FASTAPI_URL}/analyze-report`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        // REMOVE LOADING MESSAGE
        chatbotMessages.removeChild(chatbotMessages.lastChild);
        appendMessage(data.response, "bot");
      }

      catch(error) {
        console.error(error);
        chatbotMessages.removeChild(chatbotMessages.lastChild);

        appendMessage("Sorry, report analysis is unavailable right now.", "bot");
      }

      // RESET INPUT
      reportFileInput.value = "";
    });
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
