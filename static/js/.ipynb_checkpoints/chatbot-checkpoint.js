let uploadedCardProfile = null;

window.addEventListener("DOMContentLoaded", () => {
  appendMessage(
    "bot",
    "Namaste! I'm Poshan Sahayak, your Anganwadi child nutrition companion.\n\nWe can talk through any child's growth concerns, symptoms like loose motions or anemia, budget meal ideas for any Indian state, or discuss any of the 18+ registered children in our directory. You can also upload a PDF Health Card above whenever you'd like. How can I help today?"
  );
});

function appendMessage(sender, text) {
  const container = document.getElementById("chat-messages");
  const bubble = document.createElement("div");
  bubble.className = `msg ${sender}`;
  bubble.textContent = text;
  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function sendQuickPrompt(promptText) {
  document.getElementById("chat-user-input").value = promptText;
  handleChatSubmit(new Event("submit"));
}

function saveGroqKey() {
  const key = document.getElementById("groq-api-key").value.trim();
  if (key) {
    localStorage.setItem("poshandrishti_groq_key", key);
    appendMessage("bot", "Got it—I've connected your live Groq AI key for this session. Let's continue our discussion!");
  }
}

// Sends uploaded PDF/TXT Health Card to Python Flask (/api/parse-card via pypdf)
async function handleHealthCardUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/api/parse-card", {
    method: "POST",
    body: formData
  });
  const data = await res.json();

  if (!res.ok) {
    appendMessage("bot", "I couldn't read that file—please try a text-based PDF or TXT health card, or tell me the child's vitals directly!");
    return;
  }

  uploadedCardProfile = data.profile;
  const badge = document.getElementById("active-card-badge");
  badge.style.display = "inline-block";
  badge.textContent = `🪪 Active Card: ${uploadedCardProfile.name} (${uploadedCardProfile.status})`;
  document.getElementById("clear-card-btn").style.display = "inline-block";

  appendMessage(
    "bot",
    `I've just reviewed ${uploadedCardProfile.name}'s Health Card via our Python document reader.\n\n${uploadedCardProfile.name} is ${uploadedCardProfile.age} months old from ${uploadedCardProfile.state}, currently in the ${uploadedCardProfile.status} zone (Z-Score: ${uploadedCardProfile.zScore}) with a daily meal budget of ${uploadedCardProfile.cost}.\n\nWould you like me to put together a full 3-meal daily chart for ${uploadedCardProfile.name}, or discuss specific feeding tips for home?`
  );
}

function clearUploadedCard() {
  uploadedCardProfile = null;
  document.getElementById("active-card-badge").style.display = "none";
  document.getElementById("clear-card-btn").style.display = "none";
  document.getElementById("card-upload-input").value = "";
  appendMessage("bot", "I've cleared that health card from our session. Feel free to ask about any other child or nutrition topic!");
}

async function handleChatSubmit(e) {
  e.preventDefault();
  const inputEl = document.getElementById("chat-user-input");
  const userText = inputEl.value.trim();
  if (!userText) return;

  appendMessage("user", userText);
  inputEl.value = "";

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: userText,
      cardProfile: uploadedCardProfile,
      apiKey: localStorage.getItem("poshandrishti_groq_key")
    })
  });
  const data = await res.json();
  appendMessage("bot", data.reply);
}
