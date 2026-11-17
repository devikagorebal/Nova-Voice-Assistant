# 🌌 Nova / Ultra Jarvis Suite — Hybrid Windows AI Assistant

A comprehensive, next-generation AI assistant built specifically for **Windows**, incorporating **all 32 modules and features** from `Document from G Devika (1)`.

Nova unites native Windows hardware automation, computer vision biometric security, generative AI (Gemini Text + Imagen), offline rule-based knowledge, multi-language translation, offline games, and mobile network companion access into a single unified desktop suite.

---

## ⚡ Quick Start

### 1. Launch the Desktop Application
Open PowerShell or Command Prompt in this folder and run:
```bash
python nova_ultra_suite.py
```
> **Note:** The entire core suite runs using **pure Python 3, Tkinter, and Pillow** with zero dependency crashes! All third-party libraries (`cv2`, `pyttsx3`, `vosk`, `requests`) have graceful native Windows fallbacks built-in.

### 2. (Optional) Launch the Mobile Companion Web Hub (Part 29)
In a second terminal window, run:
```bash
python server.py
```
Access the mobile companion dashboard from any phone or browser on your local WiFi at:
`http://localhost:8765` or `http://<your-pc-ip>:8765`

---

## 📋 Comprehensive Feature Map (All 32 Parts)

| Part | Feature Module | Capabilities & How It Works |
|---|---|---|
| **Core (1–15)** | **Online + Offline Hybrid Engine** | Auto-switches between Online Mode (Gemini AI, Google Search, YouTube) and Offline Mode (local apps, offline notes, offline math, offline games). |
| **Security** | **Biometric Face Lock (OpenCV)** | Live webcam face verification using Haar Cascades + grayscale comparison scoring (`score < threshold`). Auto-prompts for PIN if face does not match or camera is off. |
| **Security** | **Face Registration & PIN System** | GUI camera face registration tool saving `registered_face.png`. Master PIN fallback with verification and change PIN dialog. |
| **Generative AI** | **Gemini AI (Text & Multilingual)** | REST API queries using Google Gemini (`gemini-2.5-flash`, `gemini-pro`) with configurable language steering (English, Hindi, Kannada, Marathi, Tamil). |
| **Generative AI** | **Gemini Imagen Image Generator** | Dedicated tab to enter prompts, generate high-res 1024x1024 PNG images, view instant Pillow `ImageTk` previews, and send them to Telegram. |
| **Speech** | **SAPI5 Safe TTS Engine** | Thread-safe Text-to-Speech with lock, previous speech cancellation, error recovery, custom voice speed, and native Windows PowerShell speech fallback. |
| **Speech** | **Speech Recognition (Online & Vosk Offline)** | Google Speech Recognition + offline Vosk speech model support (`TARANGA` folder) + Siri-style continuous wake-word listener. |
| **Visuals** | **Animated Robot Window** | Floating canvas robot with glowing eyes, animated mouth, 12 audio visualizer bars, and 3 color palettes (Blue Neon, Amber Gold, Mint Emerald). |
| **UI** | **8 Dynamic Color Themes** | Instant switching between Dark, Light, Neon, Red Nova, Purple Galaxy, Emerald, Gold Lux, and Cyber Pink. |
| **Productivity** | **Notes & To-Do Tabs** | Full notes editor with persistent storage and task manager with completion marks. |
| **Productivity** | **Alarms & Reminders** | Reminders with Windows chimes, alert popups, automated command execution, and Telegram image sending actions (`image: <prompt>`). |
| **Part 16** | **System Commands** | Shutdown in 10s (`shutdown /s /t 10`), restart in 10s, workstation lock (`user32.LockWorkStation`), and screen capture. |
| **Part 17** | **Offline Games** | Interactive GUI **Tic-Tac-Toe** (Player X vs AI O) and **Number Guessing Game** with hints. |
| **Part 18** | **Emotion Detection** | Webcam scanner detecting facial emotions (Smiling/Happy 😊 vs Neutral/Calm 😐). |
| **Part 19** | **Offline Chess GUI** | 8x8 Tkinter chessboard with piece moving logic. |
| **Part 20** | **Multi-Telegram Bots & Logging** | Dispatches text and photos to Telegram bot tokens and logs events with timestamps to `jarvis_logs.txt`. |
| **Part 21** | **Plugin Extension System** | Dynamic loader scanning `plugins/` directory and auto-binding custom command handlers. |
| **Part 22** | **Voice Personality Packs** | Switchable personality modes: **Normal**, **Friendly**, **Jarvis Butler**, **Sarcastic**, **Boss**, **Anime**. |
| **Part 23** | **Full Offline AI** | Rule-based and memory-based question answering, arithmetic math calculator, and identity help when offline. |
| **Part 24** | **Offline Local LLM Fallback** | Architecture support for local GGUF models via llama.cpp or local Ollama REST (`http://localhost:11434`). |
| **Part 25** | **Voice Cloning** | Local voice sample recording and cloning engine hook (`models/voice/user.wav`). |
| **Part 26** | **Auto-Updater** | Version checking against remote JSON release index. |
| **Part 27** | **Plugin Marketplace** | Remote plugin index browser and 1-click installer into `plugins/`. |
| **Part 28** | **Encrypted Memory Vault** | Fernet AES-256 (with PBKDF2 stream cipher fallback) storing confidential memory in `jarvis_vault.bin`. |
| **Part 29** | **Mobile Companion API** | Multi-threaded HTTP server (port 8765) with REST endpoints and responsive web UI for mobile devices. |
| **Part 30** | **Permissions & Sandboxing** | Fine-grained permission controls (`system_power`, `file_ops`, `webcam`, `shell_cmd`, `network_requests`, `mobile_api`). |
| **Part 31** | **Task Scheduler** | Cron-like scheduler supporting `every N min` intervals and daily schedules with persistence. |
| **Part 32** | **Desktop Floating Widgets** | Top-level always-on Desktop Clock Widget, System Resource Monitor Widget (CPU/RAM/Battery), and Mini Assistant. |

---

## 🎙️ Voice & Command Cheat Sheet

| Category | Example Commands |
|---|---|
| **AI Intelligence** | `"ask what is the theory of relativity"`, `"who is Nikola Tesla"`, `"calculate 45 * 18"` |
| **Multi-Language** | `"set language hindi"`, `"set language kannada"`, `"set language tamil"`, `"set language marathi"`, `"set language english"` |
| **System Automation** | `"volume up"`, `"volume down"`, `"mute"`, `"lock pc"`, `"take a screenshot"`, `"check battery"` |
| **Launch Apps** | `"open calculator"`, `"open notepad"`, `"open explorer"`, `"open settings"`, `"open music"` |
| **Reminders** | `"remind me at 5 pm to study physics"`, `"remind me at 18:30 to join meeting"` |
| **Games & Vision** | `"play game"`, `"tic tac toe"`, `"chess"`, `"detect emotion"` |
| **Themes & Styles** | `"toggle theme"`, or click the **🎨 Theme** button in the header bar |
| **Personalities** | `"set personality friendly"`, `"set personality jarvis"`, `"set personality sarcastic"` |
| **Power Operations** | `"shutdown system"`, `"restart system"` |

---

## 📁 Project Architecture

```text
nova-ultra-suite/
├── nova_ultra_suite.py     # Unified Master Desktop Application (Parts 1-32)
├── server.py               # Mobile Companion API & Web Dashboard Server (Part 29)
├── requirements.txt        # Optional dependencies guide
├── README.md               # Documentation & command reference
├── data/                   # Persistent data directory
│   ├── memory.json         # Settings, theme, language, and memory
│   ├── reminders.json      # Active reminders
│   ├── jarvis_schedule.json# Task scheduler jobs
│   ├── jarvis_password.json# Security PIN hash
│   ├── jarvis_logs.txt     # Audit log
│   └── registered_face.png # Biometric face reference
├── plugins/                # Dynamic plugins directory (Part 21)
│   ├── weather_plugin.py   # Sample weather forecast plugin
│   └── crypto_plugin.py    # Sample cryptocurrency price tracker plugin
├── generated_images/       # Generated Gemini Imagen PNG images
└── static/                 # Mobile Companion Web Assets (Part 29)
    ├── index.html          # Web companion UI
    ├── style.css           # Glassmorphic dark styling
    └── script.js           # Web Speech API & Fetch API client
```

---

## 🔒 Security & Biometrics Configuration

1. **Biometric Face Lock**:
   - Click **⚙️ Settings** → **📸 Register Face (Camera)**.
   - Look at the webcam and press **SPACE** to capture your face.
   - When launching `nova_ultra_suite.py`, Nova verifies your face. If camera is off or face is unrecognized, it automatically opens the secure **PIN entry dialog** (Default PIN: `1234`).
2. **Change Master PIN**:
   - In Settings, click **🔑 Change PIN** to update your security password.
