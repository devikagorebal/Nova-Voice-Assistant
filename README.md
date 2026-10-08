# 🌌 Nova - Siri-like Voice Assistant for Windows

An intelligent desktop voice assistant tailored specifically for **Windows**, built using **pure Python**, **HTML5**, **CSS3**, and **JavaScript** with **zero external web frameworks** (no Flask, no Django) and **zero pip package installations required**!

---

## 🚀 Key Highlights

1. **Prominent Conversation Feed**:
   - The UI displays an expansive, high-contrast, beautiful conversation stream in the center of the screen.
   - Shows user inputs on the right (vibrant gradient bubble) and Nova responses on the left (glassmorphic card with system badges and audio playback).
   - Auto-scrolls so the latest conversation is always visible.
2. **Zero User API Key Friction**:
   - You are never asked to enter an API key in the UI. Everything works out of the box.
3. **AI Integration Specifically for Google Search**:
   - When you say `"Search Google for..."`, `"Google..."`, or ask questions like `"Who is..."` or `"What is..."`, Nova queries the AI engine to generate an instant concise answer while also opening Google search in your browser.
   - All standard Windows tasks (opening applications, adjusting volume, checking battery, locking the workstation, taking screenshots, date/time, and taking notes) run locally and instantly without needing any API.
4. **Siri-Style Ambient Experience**:
   - Compact glowing Siri orb in the top header that reacts with pulsing animations when listening, thinking, and speaking.
   - Synchronized audio wave visualizer.
   - Reads replies aloud using Windows desktop Speech Synthesis with customizable voices and speed.

---

## 📁 Project Structure

```text
nova-assistant/
├── server.py            # Pure Python HTTP server (threading, static assets, APIs)
├── system_control.py    # Native Windows controls (ctypes, PowerShell, apps)
├── ai_engine.py         # AI engine for Google search commands & instant knowledge
├── command_handler.py   # Intent parsing and command dispatch
├── index.html           # Modern UI with prominent conversation view
├── style.css            # Dark glassmorphism theme with high-contrast chat bubbles
├── script.js            # Web Speech API recognition & speech synthesis
└── README.md            # Documentation
```

---

## ⚡ How to Run

1. Open PowerShell or Command Prompt in the project folder:
   ```bash
   cd C:\Users\HP\.gemini\antigravity\scratch\nova-assistant
   ```
2. Start Nova using standard Python:
   ```bash
   python server.py
   ```
3. Your default web browser will automatically open:
   ```
   http://localhost:8000
   ```
4. Click the **Microphone** icon to talk with Nova or type in the input bar below!

---

## 🎙️ Example Voice & Text Commands

| Category | Example Commands |
|---|---|
| **AI Google Search** | `"Search Google for who is the CEO of Apple"`, `"Google quantum computing"`, `"Who was Nikola Tesla?"` |
| **Volume Control** | `"Increase volume"`, `"Turn down volume"`, `"Mute sound"` |
| **System Info & Power** | `"Check battery"`, `"Lock my PC"`, `"Take a screenshot"` |
| **Launch Applications** | `"Open Calculator"`, `"Open Notepad"`, `"Open Task Manager"`, `"Open Settings"` |
| **Date & Time** | `"What time is it?"`, `"What is today's date?"` |
| **Voice Notes** | `"Take a note meeting tomorrow at 3 PM"`, `"Show my notes"`, `"Clear notes"` |
| **Web & Media** | `"Search YouTube for lofi beats"`, `"Open GitHub"`, `"Open Reddit"` |
| **Everyday Assistance** | `"Calculate 145 * 25"`, `"Tell me a joke"`, `"What can you do?"` |

---

## ⚙️ Optional Gemini API Key for Search

If you want to use your own Google Gemini API key for Google search commands, simply set the environment variable:
```bash
set GEMINI_API_KEY=your_key_here
```
Or define `GEMINI_API_KEY = "your_key_here"` at the top of `ai_engine.py`. Even without a key, Nova uses built-in live web search to deliver instant factual answers!
