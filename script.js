/**
 * script.js - Nova Voice Assistant Front-End Controller
 * Pure JavaScript using Web Speech API (Recognition + Synthesis) & Fetch API
 */

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const micBtn = document.getElementById("micBtn");
    const orbWrapper = document.getElementById("orbWrapper");
    const statusLabel = document.getElementById("statusLabel");
    const waveContainer = document.getElementById("waveContainer");
    const commandInput = document.getElementById("commandInput");
    const sendBtn = document.getElementById("sendBtn");
    const chatStream = document.getElementById("chatStream");
    const conversationView = document.getElementById("conversationView");
    const batteryText = document.getElementById("batteryText");
    const transcriptBanner = document.getElementById("transcriptBanner");
    const transcriptText = document.getElementById("transcriptText");

    // Modals
    const notesBtn = document.getElementById("notesBtn");
    const notesModal = document.getElementById("notesModal");
    const closeNotesBtn = document.getElementById("closeNotesBtn");
    const notesListContainer = document.getElementById("notesListContainer");
    const clearNotesBtn = document.getElementById("clearNotesBtn");

    const settingsBtn = document.getElementById("settingsBtn");
    const settingsModal = document.getElementById("settingsModal");
    const closeSettingsBtn = document.getElementById("closeSettingsBtn");
    const saveSettingsBtn = document.getElementById("saveSettingsBtn");
    const voiceToggle = document.getElementById("voiceToggle");
    const voiceSelect = document.getElementById("voiceSelect");
    const speechRate = document.getElementById("speechRate");
    const rateVal = document.getElementById("rateVal");

    // State
    let isListening = false;
    let recognition = null;
    let voices = [];
    let voiceOutputEnabled = localStorage.getItem("nova_voice_enabled") !== "false";
    let currentRate = parseFloat(localStorage.getItem("nova_voice_rate") || "1.0");

    voiceToggle.checked = voiceOutputEnabled;
    speechRate.value = currentRate;
    rateVal.textContent = `${currentRate.toFixed(1)}x`;

    // 1. Web Speech Recognition
    function initSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            statusLabel.textContent = "Voice input unavailable (type below)";
            micBtn.style.opacity = "0.5";
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            isListening = true;
            micBtn.classList.add("active");
            orbWrapper.classList.add("listening");
            waveContainer.classList.add("active");
            statusLabel.textContent = "Listening to your voice...";
            transcriptBanner.classList.add("visible");
            transcriptText.textContent = "Listening...";
        };

        recognition.onresult = (event) => {
            let interimTranscript = "";
            let finalTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }

            const current = finalTranscript || interimTranscript;
            if (current) {
                transcriptText.textContent = `"${current}"`;
            }

            if (finalTranscript) {
                transcriptBanner.classList.remove("visible");
                handleSendCommand(finalTranscript.trim());
            }
        };

        recognition.onerror = (e) => {
            stopListening();
            statusLabel.textContent = "Voice error • Click to retry";
        };

        recognition.onend = () => {
            stopListening();
        };
    }

    function startListening() {
        if (!recognition) return;
        window.speechSynthesis.cancel();
        try {
            recognition.start();
        } catch (e) {}
    }

    function stopListening() {
        isListening = false;
        micBtn.classList.remove("active");
        orbWrapper.classList.remove("listening");
        waveContainer.classList.remove("active");
        transcriptBanner.classList.remove("visible");
        if (!window.speechSynthesis.speaking) {
            statusLabel.textContent = "Ready • Click mic or speak";
        }
    }

    micBtn.addEventListener("click", () => {
        if (isListening) {
            if (recognition) recognition.stop();
        } else {
            startListening();
        }
    });

    orbWrapper.addEventListener("click", () => {
        if (!isListening) startListening();
        else if (recognition) recognition.stop();
    });

    // 2. Speech Synthesis
    function initVoices() {
        if (!window.speechSynthesis) return;

        function loadVoices() {
            voices = window.speechSynthesis.getVoices();
            voiceSelect.innerHTML = '<option value="">Default Windows Voice</option>';
            const savedVoiceName = localStorage.getItem("nova_voice_name");

            voices.forEach((v, idx) => {
                if (v.lang.startsWith("en")) {
                    const opt = document.createElement("option");
                    opt.value = idx;
                    opt.textContent = `${v.name} (${v.lang})`;
                    if (savedVoiceName && v.name === savedVoiceName) {
                        opt.selected = true;
                    }
                    voiceSelect.appendChild(opt);
                }
            });
        }

        loadVoices();
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = loadVoices;
        }
    }

    function speakText(text) {
        if (!voiceOutputEnabled || !window.speechSynthesis) return;

        window.speechSynthesis.cancel();

        // Strip urls, symbols, and formatting for audio
        const cleanText = text
            .replace(/https?:\/\/\S+/g, "")
            .replace(/[*_#`~\[\]]/g, "")
            .trim();

        if (!cleanText) return;

        const utterance = new SpeechSynthesisUtterance(cleanText);
        const selIdx = voiceSelect.value;
        if (selIdx !== "" && voices[selIdx]) {
            utterance.voice = voices[selIdx];
        }

        utterance.rate = currentRate;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
            orbWrapper.classList.add("speaking");
            waveContainer.classList.add("active");
            statusLabel.textContent = "Nova is speaking...";
        };

        utterance.onend = () => {
            orbWrapper.classList.remove("speaking");
            waveContainer.classList.remove("active");
            statusLabel.textContent = "Ready • Click mic or speak";
        };

        utterance.onerror = () => {
            orbWrapper.classList.remove("speaking");
            waveContainer.classList.remove("active");
            statusLabel.textContent = "Ready • Click mic or speak";
        };

        window.speechSynthesis.speak(utterance);
    }

    // 3. Command Processing & UI Appending
    async function handleSendCommand(commandText) {
        if (!commandText || !commandText.trim()) return;

        // Render user message immediately
        appendUserMessage(commandText);
        commandInput.value = "";
        statusLabel.textContent = "Nova is processing...";

        try {
            const response = await fetch("/api/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ command: commandText })
            });

            if (!response.ok) throw new Error("Server error");

            const data = await response.json();
            const reply = data.response || "Command executed.";

            // Render assistant response clearly in conversation stream
            appendAssistantMessage(reply, data);
            speakText(reply);

            if (data.action === "battery") {
                updateBatteryStatus();
            }
        } catch (err) {
            console.error("Error communicating with assistant:", err);
            const errReply = "I could not communicate with the Windows assistant server.";
            appendAssistantMessage(errReply, { action: "error" });
            speakText(errReply);
        }
    }

    // Append User Message to visible conversation feed
    function appendUserMessage(text) {
        const row = document.createElement("div");
        row.className = "message-row user-row";

        const avatar = document.createElement("div");
        avatar.className = "msg-avatar";
        avatar.textContent = "👤";

        const bubble = document.createElement("div");
        bubble.className = "msg-bubble user-bubble";

        const content = document.createElement("div");
        content.className = "msg-content";
        content.textContent = text;

        bubble.appendChild(content);
        row.appendChild(avatar);
        row.appendChild(bubble);

        chatStream.appendChild(row);
        scrollToBottom();
    }

    // Append Assistant Message to visible conversation feed
    function appendAssistantMessage(text, metadata = {}) {
        const row = document.createElement("div");
        row.className = "message-row assistant-row";

        const isAiSearch = metadata.action === "google_search";
        const avatar = document.createElement("div");
        avatar.className = "msg-avatar";
        avatar.textContent = isAiSearch ? "🌐" : "✨";

        const bubble = document.createElement("div");
        bubble.className = "msg-bubble assistant-bubble" + (isAiSearch ? " ai-highlight" : "");

        // Header info
        const header = document.createElement("div");
        header.className = "msg-header";

        const senderName = document.createElement("span");
        senderName.className = "sender-name";
        senderName.textContent = "Nova";

        const actionTag = document.createElement("span");
        actionTag.className = "action-tag" + (isAiSearch ? " ai-tag" : "");

        const actionTitles = {
            "google_search": "AI Google Search",
            "volume_up": "Volume +",
            "volume_down": "Volume -",
            "volume_mute": "Mute",
            "lock": "PC Locked",
            "battery": "Battery Info",
            "screenshot": "Screenshot Saved",
            "time": "Date & Time",
            "note_add": "Note Saved",
            "note_view": "Notes",
            "note_clear": "Notes Cleared",
            "youtube": "YouTube",
            "wikipedia": "Wikipedia",
            "app_open": "Application",
            "website": "Web Link",
            "general_reply": "Assistant"
        };
        actionTag.textContent = actionTitles[metadata.action] || "Assistant";

        header.appendChild(senderName);
        header.appendChild(actionTag);
        bubble.appendChild(header);

        // Content
        const content = document.createElement("div");
        content.className = "msg-content";
        content.innerHTML = escapeHtml(text);
        bubble.appendChild(content);

        // Search link if applicable
        if (metadata.search_url) {
            const link = document.createElement("a");
            link.className = "msg-footer-link";
            link.href = metadata.search_url;
            link.target = "_blank";
            link.textContent = "↗ Open full Google search in browser";
            bubble.appendChild(link);
        }

        row.appendChild(avatar);
        row.appendChild(bubble);
        chatStream.appendChild(row);
        scrollToBottom();
    }

    function scrollToBottom() {
        setTimeout(() => {
            conversationView.scrollTop = conversationView.scrollHeight;
        }, 50);
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\n/g, "<br>");
    }

    // 4. Input Events
    sendBtn.addEventListener("click", () => {
        handleSendCommand(commandInput.value);
    });

    commandInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleSendCommand(commandInput.value);
        }
    });

    // Quick chips & sample buttons
    document.addEventListener("click", (e) => {
        const chip = e.target.closest(".chip") || e.target.closest(".sample-btn");
        if (chip) {
            const cmd = chip.getAttribute("data-cmd");
            if (cmd) handleSendCommand(cmd);
        }
    });

    // 5. Battery & Status Polling
    async function updateBatteryStatus() {
        try {
            const res = await fetch("/api/status");
            if (res.ok) {
                const data = await res.json();
                if (data.battery) {
                    const match = data.battery.match(/(\d+)%/);
                    batteryText.textContent = match ? `${match[1]}%` : "AC Power";
                }
            }
        } catch (e) {
            batteryText.textContent = "Active";
        }
    }

    // 6. Notes Modal
    notesBtn.addEventListener("click", async () => {
        notesModal.classList.add("open");
        loadNotes();
    });

    closeNotesBtn.addEventListener("click", () => notesModal.classList.remove("open"));

    async function loadNotes() {
        try {
            const res = await fetch("/api/notes");
            const data = await res.json();
            const notes = data.notes || [];

            if (notes.length === 0) {
                notesListContainer.innerHTML = '<p class="empty-state">No notes saved yet. Say "Take a note [text]" to record one!</p>';
                return;
            }

            notesListContainer.innerHTML = notes.map(n => `
                <div class="note-card">
                    <div>${escapeHtml(n.text)}</div>
                    <small>${escapeHtml(n.timestamp)}</small>
                </div>
            `).join("");
        } catch (e) {
            notesListContainer.innerHTML = '<p class="empty-state">Unable to load notes.</p>';
        }
    }

    clearNotesBtn.addEventListener("click", async () => {
        if (confirm("Are you sure you want to clear all notes?")) {
            await fetch("/api/notes/clear", { method: "POST" });
            loadNotes();
        }
    });

    // 7. Voice Settings Modal (Zero API Key prompts)
    settingsBtn.addEventListener("click", () => {
        settingsModal.classList.add("open");
    });

    closeSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("open"));

    speechRate.addEventListener("input", (e) => {
        currentRate = parseFloat(e.target.value);
        rateVal.textContent = `${currentRate.toFixed(1)}x`;
        localStorage.setItem("nova_voice_rate", currentRate.toString());
    });

    voiceToggle.addEventListener("change", (e) => {
        voiceOutputEnabled = e.target.checked;
        localStorage.setItem("nova_voice_enabled", voiceOutputEnabled.toString());
    });

    voiceSelect.addEventListener("change", (e) => {
        const selIdx = e.target.value;
        if (selIdx !== "" && voices[selIdx]) {
            localStorage.setItem("nova_voice_name", voices[selIdx].name);
        }
    });

    saveSettingsBtn.addEventListener("click", () => {
        settingsModal.classList.remove("open");
    });

    // Close on backdrop click
    [notesModal, settingsModal].forEach(m => {
        m.addEventListener("click", (e) => {
            if (e.target === m) m.classList.remove("open");
        });
    });

    // Initialization
    initSpeechRecognition();
    initVoices();
    updateBatteryStatus();
});
