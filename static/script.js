document.addEventListener("DOMContentLoaded", () => {
    const cmdInput = document.getElementById("cmdInput");
    const sendBtn = document.getElementById("sendBtn");
    const micBtn = document.getElementById("micBtn");
    const chatStream = document.getElementById("chatStream");

    // Speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            handleCommand(text);
        };
        recognition.onerror = () => micBtn.classList.remove("active");
        recognition.onend = () => micBtn.classList.remove("active");
    }

    micBtn.addEventListener("click", () => {
        if (!recognition) return alert("Web Speech API not supported on this browser.");
        micBtn.classList.add("active");
        recognition.start();
    });

    async function handleCommand(text) {
        if (!text || !text.trim()) return;
        appendMessage("user", text);
        cmdInput.value = "";

        try {
            const res = await fetch("/api/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: jsonString({ command: text })
            });
            const data = await res.json();
            const reply = data.response || "Executed.";
            appendMessage("assistant", reply);
            if (window.speechSynthesis) {
                window.speechSynthesis.speak(new SpeechSynthesisUtterance(reply));
            }
        } catch (e) {
            appendMessage("assistant", "Server communication error.");
        }
    }

    function jsonString(obj) {
        return JSON.stringify(obj);
    }

    function appendMessage(sender, text) {
        const row = document.createElement("div");
        row.className = `msg ${sender}-msg`;
        const avatar = document.createElement("div");
        avatar.className = "avatar";
        avatar.textContent = sender === "user" ? "👤" : "⚡";
        const bubble = document.createElement("div");
        bubble.className = "bubble";
        bubble.textContent = text;
        row.appendChild(avatar);
        row.appendChild(bubble);
        chatStream.appendChild(row);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    sendBtn.addEventListener("click", () => handleCommand(cmdInput.value));
    cmdInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleCommand(cmdInput.value);
    });

    document.querySelectorAll(".pill").forEach(p => {
        p.addEventListener("click", () => handleCommand(p.getAttribute("data-cmd")));
    });
});
