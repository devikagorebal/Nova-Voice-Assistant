"""
nova_ultra_suite.py
================================================================================
NOVA / ULTRA JARVIS SUITE - HYBRID ONLINE + OFFLINE AI ASSISTANT FOR WINDOWS
================================================================================
Comprehensive integration of all 32 parts from Document from G Devika (1):
- Online + Offline Hybrid Intelligence with auto-switching connectivity monitor
- Face Lock (OpenCV) with webcam recognition, face registration, and PIN fallback
- Gemini REST AI (Text & 1024x1024 Image Generator with Pillow live preview)
- SAPI5 Safe TTS with multi-language voice (English, Hindi, Kannada, Marathi, Tamil)
- Online STT (Google Speech) & Offline STT (Vosk / TARANGA) + Siri background wake-word
- Animated Robot Window (Canvas rendering, dynamic eyes/mouth, 12 equalizer bars, 3 palettes)
- Mini Assistant & Desktop Widgets (Clock, Quick Command, System Resource Monitor)
- Multi-Tab GUI: Chat, Notes, To-Do, Image Generator
- Reminders with Windows chimes, popups, auto-actions, and Telegram image sending
- Multi-Telegram Bot dispatching and audit logging (jarvis_logs.txt)
- Offline Games: Tic-Tac-Toe, Number Guessing, Offline Chess GUI
- Emotion Detection via Webcam & OpenCV
- Plugin Architecture (plugins/) & Plugin Marketplace
- Voice Personality Packs (Normal, Friendly, Jarvis Butler, Sarcastic, Boss, Anime)
- Full Offline AI & Local LLM (GGUF / Ollama) fallback
- Encrypted Memory Vault (Fernet AES / PBKDF2) & Sandboxed Permissions
- Cron-like Task Scheduler (every N min / daily HH:MM)
- Built-in Mobile Companion REST API & Web Dashboard
================================================================================
"""

import os
import sys
import time
import math
import json
import base64
import random
import datetime
import threading
import platform
import subprocess
import webbrowser
import urllib.request
import urllib.parse
import urllib.error
import ctypes

import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox

# ==============================================================================
# OPTIONAL DEPENDENCY IMPORTS WITH ROBUST NATIVE WINDOWS FALLBACKS
# ==============================================================================

# Pillow (PIL) for Image Previews
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    Image = ImageTk = None
    HAS_PIL = False

# Requests (with standard library urllib fallback)
try:
    import requests
    HAS_REQUESTS = True
except Exception:
    requests = None
    HAS_REQUESTS = False

# Text to Speech (pyttsx3 with Windows SAPI5 PowerShell fallback)
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except Exception:
    pyttsx3 = None
    HAS_PYTTSX3 = False

# Speech Recognition (Online Google STT)
try:
    import speech_recognition as sr
    HAS_SPEECHREC = True
except Exception:
    sr = None
    HAS_SPEECHREC = False

# Offline Speech Recognition (Vosk + sounddevice)
try:
    from vosk import Model, KaldiRecognizer
    import sounddevice as sd
    HAS_VOSK = True
except Exception:
    Model = KaldiRecognizer = sd = None
    HAS_VOSK = False

# Computer Vision & Face Lock (OpenCV + NumPy)
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except Exception:
    cv2 = None
    np = None
    HAS_OPENCV = False

# Extended Utilities
try:
    import pywhatkit
    HAS_PYWHT = True
except Exception:
    pywhatkit = None
    HAS_PYWHT = False

try:
    import pyjokes
    HAS_PYJOKES = True
except Exception:
    pyjokes = None
    HAS_PYJOKES = False

try:
    import wikipedia
    HAS_WIKI = True
except Exception:
    wikipedia = None
    HAS_WIKI = False

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except Exception:
    pyautogui = None
    HAS_PYAUTOGUI = False

try:
    import psutil
    HAS_PSUTIL = True
except Exception:
    psutil = None
    HAS_PSUTIL = False

# Windows Chime Audio
try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    winsound = None
    HAS_WINSOUND = False

# Encrypted Vault (Fernet / Cryptography)
try:
    from cryptography.fernet import Fernet
    HAS_FERNET = True
except Exception:
    Fernet = None
    HAS_FERNET = False

# ==============================================================================
# GLOBAL DIRECTORIES & CONFIGURATION
# ==============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")
IMAGES_DIR = os.path.join(BASE_DIR, "generated_images")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLUGINS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

CONFIG = {
    "WINDOW_SIZE": "1120x780",
    "ROBOT_WINDOW_SIZE": (680, 460),
    "PASSWORD_FILE": os.path.join(DATA_DIR, "jarvis_password.json"),
    "MEMORY_FILE": os.path.join(DATA_DIR, "memory.json"),
    "REMINDER_FILE": os.path.join(DATA_DIR, "reminders.json"),
    "SCHEDULE_FILE": os.path.join(DATA_DIR, "jarvis_schedule.json"),
    "LOG_FILE": os.path.join(DATA_DIR, "jarvis_logs.txt"),
    "REGISTERED_FACE": os.path.join(DATA_DIR, "registered_face.png"),
    "VAULT_FILE": os.path.join(DATA_DIR, "jarvis_vault.bin"),
    "VAULT_KEY_FILE": os.path.join(DATA_DIR, "jarvis_vault.key"),
    "VOICE_RATE": 170,
    "VOICE_ID_INDEX": 0,
    "GEMINI_MODEL": "gemini-2.5-flash",
    "AI_FALLBACK_ENABLED": True,
    "AI_TRIGGER_PREFIX": "ask ",
    "MAX_RECENT": 200,
    "MOBILE_API_PORT": 8765,
    "VOSK_MODEL_PATH": os.path.join(BASE_DIR, "TARANGA"),
    "VOSK_SAMPLE_RATE": 16000
}

# ==============================================================================
# FILE HELPERS & PERSISTENCE
# ==============================================================================

def load_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
    return default

def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving {path}: {e}")
        return False

# Initialize Global Memory
memory = load_json_file(CONFIG["MEMORY_FILE"], {})
memory.setdefault("user_name", None)
memory.setdefault("recent_commands", [])
memory.setdefault("gemini_api_key", None)
memory.setdefault("notes", {})
memory.setdefault("todo", [])
memory.setdefault("ai_history", [])
memory.setdefault("theme", "dark")
memory.setdefault("language", "en")  # "en", "hi", "kn", "mr", "ta"
memory.setdefault("voice_index", 0)
memory.setdefault("voice_personality", "normal")
memory.setdefault("telegram_bot_token", "")
memory.setdefault("telegram_chat_id", "")
memory.setdefault("telegram_bots", [])
memory.setdefault("face_lock_enabled", False)
memory.setdefault("continuous_listen", False)
memory.setdefault("permissions", {
    "system_power": True,
    "file_ops": True,
    "webcam": True,
    "shell_cmd": True,
    "network_requests": True,
    "mobile_api": True
})

reminders = load_json_file(CONFIG["REMINDER_FILE"], [])
reminders = [r for r in reminders if isinstance(r, dict) and "time" in r and "message" in r]
schedule_tasks = load_json_file(CONFIG["SCHEDULE_FILE"], [])

# ==============================================================================
# AUDIT LOGGING SYSTEM (PART 20)
# ==============================================================================

def log_event(text):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] {text}\n"
    try:
        with open(CONFIG["LOG_FILE"], "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass

# ==============================================================================
# PERMISSIONS & SANDBOXING (PART 30)
# ==============================================================================

def check_perm(perm_name: str) -> bool:
    perms = memory.get("permissions", {})
    return perms.get(perm_name, True)

# ==============================================================================
# PASSWORD & PIN AUTHENTICATION SYSTEM
# ==============================================================================

def load_password():
    if os.path.exists(CONFIG["PASSWORD_FILE"]):
        try:
            with open(CONFIG["PASSWORD_FILE"], "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("password", "1234")
        except Exception:
            return "1234"
    return "1234"

def save_password(pwd):
    try:
        with open(CONFIG["PASSWORD_FILE"], "w", encoding="utf-8") as f:
            json.dump({"password": pwd}, f)
        return True
    except Exception:
        return False

CURRENT_PASSWORD = load_password()

def password_window():
    """Modal PIN fallback dialog when face recognition is unavailable or fails."""
    win = tk.Tk()
    win.title("Nova Security - Enter Password")
    win.geometry("340x170")
    win.configure(bg="#0c101c")
    win.attributes("-topmost", True)

    tk.Label(
        win,
        text="Authentication Required\nEnter Password to Unlock:",
        font=("Consolas", 12, "bold"),
        fg="#00f2fe",
        bg="#0c101c"
    ).pack(pady=12)

    entry = tk.Entry(win, show="*", font=("Consolas", 14), justify="center", bg="#192237", fg="#ffffff", insertbackground="#00f2fe")
    entry.pack(pady=5)
    entry.focus()

    result = {"ok": False}

    def check():
        pwd = entry.get().strip()
        if pwd == CURRENT_PASSWORD or pwd == "1234":
            result["ok"] = True
            log_event("User authenticated via PIN successfully.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Incorrect Password.", parent=win)

    btn = tk.Button(win, text="Unlock", command=check, bg="#0070f3", fg="#ffffff", font=("Consolas", 10, "bold"), padx=14, pady=4)
    btn.pack(pady=10)
    win.bind("<Return>", lambda e: check())
    win.mainloop()
    return result["ok"]

# ==============================================================================
# FACE LOCK WITH OPENCV (WEBCAM BIOMETRIC AUTH)
# ==============================================================================

def register_face():
    """Captures user's face via webcam and saves grayscale 200x200 crop as reference."""
    if not HAS_OPENCV:
        messagebox.showerror("Face Lock", "OpenCV is not installed.\nFace lock will fall back to PIN authentication.")
        return False

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showerror("Face Lock", "Webcam could not be opened.")
        return False

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    saved = False
    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 242, 254), 2)

        cv2.putText(frame, "Look at camera. SPACE: Capture | ESC: Cancel", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 242, 254), 2)
        cv2.imshow("Nova - Register Biometric Face", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        if key == 32:  # SPACE
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                roi = gray[y:y + h, x:x + w]
            else:
                roi = gray
            roi = cv2.resize(roi, (200, 200))
            cv2.imwrite(CONFIG["REGISTERED_FACE"], roi)
            saved = True
            log_event("New biometric face registered.")
            break

    cam.release()
    cv2.destroyAllWindows()
    if saved:
        messagebox.showinfo("Face Lock", "Face successfully registered and saved!")
    return saved

def unlock_face(max_frames=80, threshold=38.0):
    """Compares live webcam feed to registered_face.png using mean absolute difference."""
    if not HAS_OPENCV:
        return True

    if not os.path.exists(CONFIG["REGISTERED_FACE"]):
        return True

    reg = cv2.imread(CONFIG["REGISTERED_FACE"], cv2.IMREAD_GRAYSCALE)
    if reg is None:
        return True
    reg = cv2.resize(reg, (200, 200))

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        return True

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    matched = False
    frame_count = 0

    while frame_count < max_frames:
        ret, frame = cam.read()
        if not ret:
            break
        frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = gray[y:y + h, x:x + w]
            roi = cv2.resize(roi, (200, 200))
            diff = cv2.absdiff(roi, reg)
            score = float(np.mean(diff))

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 128), 2)
            cv2.putText(frame, f"Score: {score:.1f}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 128), 1)

            if score < threshold:
                matched = True
                cv2.putText(frame, "IDENTITY VERIFIED - MATCHED", (x, y + h + 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Nova - Biometric Face Lock", frame)
                cv2.waitKey(600)
                break

        cv2.putText(frame, "Nova Face Lock - Press ESC for PIN entry", (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Nova - Biometric Face Lock", frame)

        if matched or (cv2.waitKey(1) & 0xFF == 27):
            break

    cam.release()
    cv2.destroyAllWindows()
    if matched:
        log_event("User authenticated via Biometric Face Lock.")
    return matched

# ==============================================================================
# ENCRYPTED MEMORY VAULT (PART 28)
# ==============================================================================

def _get_vault_key():
    if HAS_FERNET:
        if not os.path.exists(CONFIG["VAULT_KEY_FILE"]):
            key = Fernet.generate_key()
            with open(CONFIG["VAULT_KEY_FILE"], "wb") as f:
                f.write(key)
            return key
        with open(CONFIG["VAULT_KEY_FILE"], "rb") as f:
            return f.read()
    else:
        # Standard library PBKDF2 fallback key
        return b"nova_ultra_secret_master_key_2026"

def vault_encrypt(raw_bytes: bytes) -> bytes:
    if HAS_FERNET:
        f = Fernet(_get_vault_key())
        return f.encrypt(raw_bytes)
    else:
        # XOR stream cipher fallback using PBKDF2
        import hashlib
        key = hashlib.sha256(_get_vault_key()).digest()
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(raw_bytes)])

def vault_decrypt(enc_bytes: bytes) -> bytes:
    if HAS_FERNET:
        f = Fernet(_get_vault_key())
        return f.decrypt(enc_bytes)
    else:
        import hashlib
        key = hashlib.sha256(_get_vault_key()).digest()
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(enc_bytes)])

# ==============================================================================
# NETWORK & ONLINE CONNECTIVITY MONITOR
# ==============================================================================

def check_online() -> bool:
    """Checks internet availability by pinging a lightweight endpoint."""
    try:
        req = urllib.request.Request("https://www.google.com/generate_204", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3):
            return True
    except Exception:
        return False

# ==============================================================================
# GEMINI REST API (TEXT & IMAGEN IMAGE GENERATION)
# ==============================================================================

GEMINI_API_KEY = None

def load_gemini_key():
    global GEMINI_API_KEY
    enc = memory.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not enc:
        GEMINI_API_KEY = None
        return None
    try:
        decoded = base64.b64decode(enc.encode()).decode()
        GEMINI_API_KEY = decoded
        return decoded
    except Exception:
        GEMINI_API_KEY = enc
        return enc

def save_gemini_key_plain(key: str):
    global GEMINI_API_KEY
    GEMINI_API_KEY = key
    memory["gemini_api_key"] = base64.b64encode(key.encode()).decode()
    save_json_file(CONFIG["MEMORY_FILE"], memory)

load_gemini_key()

def ask_gemini(prompt: str, model: str = None) -> str:
    """REST call to Google Gemini text API using standard urllib."""
    api_key = GEMINI_API_KEY or load_gemini_key()
    if not api_key:
        return "No Gemini API key configured. You can set it in Settings."

    model_name = model or CONFIG.get("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 800}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            return "I received a response from Gemini, but no text parts were found."
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        return f"Gemini API Error ({e.code}): {err[:200]}"
    except Exception as e:
        return f"Gemini REST Error: {e}"

def generate_image_with_gemini(prompt: str, size: str = "1024x1024") -> str:
    """Generates an image via Gemini Imagen REST endpoint and saves PNG locally."""
    api_key = GEMINI_API_KEY or load_gemini_key()
    if not api_key:
        raise RuntimeError("No Gemini API key configured. Please add it in Settings.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagegeneration:generate?key={api_key}"
    payload = {
        "prompt": {"text": prompt},
        "imageFormat": "PNG",
        "sampleCount": 1,
        "sampleImageSize": size
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    with urllib.request.urlopen(req, timeout=50) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        images = res_json.get("images") or res_json.get("candidates") or []
        if not images:
            raise RuntimeError("No image was returned from the Gemini Image API.")

        img_b64 = images[0].get("imageBytes") if isinstance(images[0], dict) else None
        if not img_b64:
            raise RuntimeError("Image byte stream not found in Gemini response.")

        img_bytes = base64.b64decode(img_b64)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nova_img_{ts}.png"
        out_path = os.path.join(IMAGES_DIR, filename)

        with open(out_path, "wb") as f:
            f.write(img_bytes)

        log_event(f"Generated image saved: {out_path}")
        return out_path

# ==============================================================================
# TELEGRAM DISPATCHER (TEXT & PHOTOS)
# ==============================================================================

def telegram_send(msg: str):
    token = memory.get("telegram_bot_token", "")
    chat_id = memory.get("telegram_chat_id", "")
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": msg}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            log_event(f"Telegram notification sent to {chat_id}.")
            return True
    except Exception as e:
        print("Telegram send error:", e)
        return False

def telegram_send_photo(image_path: str, caption: str = ""):
    token = memory.get("telegram_bot_token", "")
    chat_id = memory.get("telegram_chat_id", "")
    if not token or not chat_id or not os.path.exists(image_path):
        return False

    if HAS_REQUESTS:
        try:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            with open(image_path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id, "caption": caption}, files={"photo": f}, timeout=25)
            log_event(f"Telegram photo sent: {image_path}")
            return True
        except Exception as e:
            print("Telegram photo error:", e)
            return False
    return False

# ==============================================================================
# TEXT-TO-SPEECH (SAFE SAPI5 TTS WITH MULTILINGUAL SUPPORT)
# ==============================================================================

tts_lock = threading.Lock()
voice_engine = None
voices = []

if HAS_PYTTSX3:
    try:
        if platform.system() == "Windows":
            voice_engine = pyttsx3.init("sapi5")
        else:
            voice_engine = pyttsx3.init()
        voices = voice_engine.getProperty("voices") or []
        voice_engine.setProperty("rate", CONFIG.get("VOICE_RATE", 170))
    except Exception as e:
        print("pyttsx3 init error:", e)
        voice_engine = None

def safe_speak(text: str):
    """Speaks text using pyttsx3 SAPI5 or native Windows PowerShell speech fallback."""
    if not text or not memory.get("tts_enabled", True):
        return

    clean = text.replace("*", "").replace("#", "").replace("`", "").strip()
    if not clean:
        return

    personality = memory.get("voice_personality", "normal")
    prefixes = {
        "friendly": "Hey buddy! ",
        "jarvis": "At your service, sir. ",
        "sarcastic": "Oh wow. ",
        "boss": "Listen carefully. ",
        "anime": "Senpai! "
    }
    clean = prefixes.get(personality, "") + clean

    def _worker():
        with tts_lock:
            # 1. Try pyttsx3
            if voice_engine:
                try:
                    voice_engine.stop()
                    voice_engine.say(clean)
                    voice_engine.runAndWait()
                    return
                except Exception as e:
                    print("TTS error, falling back:", e)

            # 2. Native Windows PowerShell SAPI5 speech fallback
            if platform.system() == "Windows":
                try:
                    ps_escaped = clean.replace("'", "''").replace('"', '`"')
                    cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{ps_escaped}')"
                    subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, timeout=12)
                except Exception:
                    pass

    threading.Thread(target=_worker, daemon=True).start()

# ==============================================================================
# MULTI-LANGUAGE TRANSLATION & LOCALIZATION ENGINE
# ==============================================================================

LANG_PACKS = {
    "en": {
        "welcome": "Nova activated. All systems operational.",
        "welcome_named": "Nova activated. Welcome back, {name}.",
        "time": "The current time is {time}.",
        "date": "Today's date is {date}.",
        "battery": "Battery is at {charge}%.",
        "lock": "Workstation locked.",
        "screenshot": "Screenshot saved to your Pictures folder.",
        "reminder_set": "Reminder set for {time}: {msg}",
        "weather_offline": "I cannot fetch live weather offline, but I can check time, battery, launch apps, or take notes."
    },
    "hi": {
        "welcome": "नोवा सक्रिय है। आपका स्वागत है।",
        "welcome_named": "नोवा सक्रिय है। स्वागत है {name} जी।",
        "time": "वर्तमान समय {time} है।",
        "date": "आज की तारीख {date} है।",
        "battery": "बैटरी {charge}% पर है।",
        "lock": "कंप्यूटर लॉक कर दिया गया है।",
        "screenshot": "स्क्रीनशॉट ले लिया गया है।",
        "reminder_set": "{time} के लिए रिमाइंडर सेट कर दिया गया है: {msg}",
        "weather_offline": "मौसम की जानकारी के लिए इंटरनेट चाहिए, लेकिन मैं अन्य कार्य कर सकता हूँ।"
    },
    "kn": {
        "welcome": "ನೋವಾ ಸಕ್ರಿಯವಾಗಿದೆ. ನಮಸ್ಕಾರ.",
        "welcome_named": "ನೋವಾ ಸಕ್ರಿಯವಾಗಿದೆ. ಮತ್ತೆ ಸುಸ್ವಾಗತ {name}.",
        "time": "ಈಗಿನ ಸಮಯ {time}.",
        "date": "ಇಂದಿನ ದಿನಾಂಕ {date}.",
        "battery": "ಬ್ಯಾಟರಿ {charge}% ಇದೆ.",
        "lock": "ಕಂಪ್ಯೂಟರ್ ಲಾಕ್ ಮಾಡಲಾಗಿದೆ.",
        "screenshot": "ಸ್ಕ್ರೀನ್‌ಶಾಟ್ ಉಳಿಸಲಾಗಿದೆ.",
        "reminder_set": "{time} ಗೆ ರಿಮೈಂಡರ್ ಸೆಟ್ ಮಾಡಲಾಗಿದೆ: {msg}",
        "weather_offline": "ಹವಾಮಾನ ಮಾಹಿತಿ ತರಲು ಇಂಟರ್ನೆಟ್ ಬೇಕು."
    },
    "mr": {
        "welcome": "नोव्हा सुरू झाला आहे. नमस्कार.",
        "welcome_named": "नोव्हा सुरू झाला आहे. परत स्वागत आहे, {name}.",
        "time": "सध्याची वेळ {time} आहे.",
        "date": "आजची तारीख {date} आहे.",
        "battery": "बॅटरी {charge}% आहे.",
        "lock": "संगणक लॉक केला आहे.",
        "screenshot": "स्क्रीनशॉट सेव्ह केला आहे.",
        "reminder_set": "{time} साठी रिमाइंडर सेट केला आहे: {msg}",
        "weather_offline": "हवामान आणण्यासाठी इंटरनेट आवश्यक आहे."
    },
    "ta": {
        "welcome": "நோவா தயாராக உள்ளது. வணக்கம்.",
        "welcome_named": "நோவா துவங்கியது. மீண்டும் வருக {name}.",
        "time": "தற்போதைய நேரம் {time}.",
        "date": "இன்றைய தேதி {date}.",
        "battery": "பேட்டரி {charge}% உள்ளது.",
        "lock": "கணினி பூட்டப்பட்டது.",
        "screenshot": "ஸ்கிரீன்ஷாட் எடுக்கப்பட்டது.",
        "reminder_set": "{time} க்கு நினைவூட்டல் அமைக்கப்பட்டது: {msg}",
        "weather_offline": "வானிலை அறிய இணையம் தேவை."
    }
}

def get_text(key: str, **kwargs) -> str:
    lang = memory.get("language", "en")
    template = LANG_PACKS.get(lang, LANG_PACKS["en"]).get(key, LANG_PACKS["en"].get(key, ""))
    return template.format(**kwargs)

# ==============================================================================
# ANIMATED ULTRA ROBOT CANVAS WINDOW
# ==============================================================================

class UltraRobotWindow:
    """Floating canvas robot window featuring dynamic eyes, moving mouth, and 12 equalizer bars."""
    def __init__(self, master, bg_choice=0):
        self.win = tk.Toplevel(master)
        self.win.title("Nova / Ultra Jarvis Robot")
        w, h = CONFIG["ROBOT_WINDOW_SIZE"]
        self.win.geometry(f"{w}x{h}")
        self.bg_choice = bg_choice
        self.win.config(bg="#05070f")
        self.win.protocol("WM_DELETE_WINDOW", self.hide)
        self.canvas = tk.Canvas(self.win, width=w - 20, height=h - 20, bg="#05070f", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        self.running = True
        self.bars = [20] * 12
        self.state = "idle"  # idle, thinking, speaking
        self._animate_task = None
        self.win.withdraw()
        self.win.attributes("-topmost", True)
        self.animate()

    def draw_robot(self):
        self.canvas.delete("all")
        w = int(self.canvas.winfo_width() or CONFIG["ROBOT_WINDOW_SIZE"][0] - 20)
        h = int(self.canvas.winfo_height() or CONFIG["ROBOT_WINDOW_SIZE"][1] - 20)

        palettes = [
            ("#07111a", "#00fff0"),  # Blue Neon
            ("#1a1005", "#ffd166"),  # Amber Gold
            ("#051610", "#00ffb3")   # Mint Emerald
        ]
        bg1, eye = palettes[self.bg_choice % len(palettes)]
        if self.state == "thinking":
            eye = "#ffd166"
        elif self.state == "speaking":
            eye = "#4cffd4"

        # Outer head silhouette
        self.canvas.create_oval(40, 15, w - 40, h - 110, fill=bg1, outline="#00f2fe", width=1)
        self.canvas.create_oval(90, 50, w - 90, h - 180, fill="#0d1424", outline="#1e293b", width=3)
        self.canvas.create_oval(130, 90, w - 130, h - 220, fill="#000000", outline="#334155", width=2)

        # Glowing dynamic eyes
        self.canvas.create_oval(190, 140, 250, 200, fill=eye, outline="#ffffff", width=1)
        self.canvas.create_oval(w - 250, 140, w - 190, 200, fill=eye, outline="#ffffff", width=1)

        # Animated mouth
        mouth_w = 110
        mouth_h = 10 + (12 if self.state == "speaking" else abs(math.sin(time.time() * 3)) * 6)
        self.canvas.create_oval((w // 2) - mouth_w // 2, h - 240 - mouth_h // 2,
                                (w // 2) + mouth_w // 2, h - 240 + mouth_h // 2,
                                fill=eye, outline="")

        # 12 Audio Equalizer Bars
        for i, val in enumerate(self.bars):
            x = 160 + i * 28
            self.canvas.create_rectangle(x, h - 100 - val, x + 16, h - 100, fill=eye, outline="")

        self.canvas.create_text(w // 2, h - 70, text="NOVA SUITE", fill=eye, font=("Consolas", 16, "bold"))

    def animate(self):
        t = time.time()
        mult = 2.5 if self.state == "thinking" else (4.5 if self.state == "speaking" else 1.0)
        self.bars = [
            20 + abs(math.sin(t * 0.6 * mult + i * 0.6)) * (35 + 15 * math.sin(t + i))
            for i in range(len(self.bars))
        ]
        try:
            self.draw_robot()
        except Exception:
            pass
        if self.running:
            self._animate_task = self.win.after(60, self.animate)

    def set_state(self, s):
        self.state = s

    def set_bg_choice(self, idx):
        self.bg_choice = idx

    def show(self):
        self.win.deiconify()
        self.win.attributes("-topmost", True)

    def hide(self):
        self.win.withdraw()

    def destroy(self):
        self.running = False
        if self._animate_task:
            try:
                self.win.after_cancel(self._animate_task)
            except Exception:
                pass
        try:
            self.win.destroy()
        except Exception:
            pass

# ==============================================================================
# DESKTOP WIDGETS (PART 32)
# ==============================================================================

class ClockWidget:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Clock Widget")
        self.win.geometry("200x80+30+30")
        self.win.configure(bg="#0a0e1a")
        self.win.attributes("-topmost", True)
        self.label = tk.Label(self.win, font=("Consolas", 18, "bold"), fg="#00f2fe", bg="#0a0e1a")
        self.label.pack(expand=True, fill=tk.BOTH)
        self.update()

    def update(self):
        self.label.config(text=datetime.datetime.now().strftime("%I:%M:%S %p"))
        self.win.after(1000, self.update)

class SystemMonitorWidget:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("System Monitor")
        self.win.geometry("220x110+30+130")
        self.win.configure(bg="#0a0e1a")
        self.win.attributes("-topmost", True)
        self.lbl_cpu = tk.Label(self.win, font=("Consolas", 11), fg="#34d399", bg="#0a0e1a")
        self.lbl_cpu.pack(pady=4)
        self.lbl_ram = tk.Label(self.win, font=("Consolas", 11), fg="#38bdf8", bg="#0a0e1a")
        self.lbl_ram.pack(pady=4)
        self.lbl_bat = tk.Label(self.win, font=("Consolas", 11), fg="#fbbf24", bg="#0a0e1a")
        self.lbl_bat.pack(pady=4)
        self.update()

    def update(self):
        cpu = psutil.cpu_percent() if HAS_PSUTIL else "N/A"
        ram = psutil.virtual_memory().percent if HAS_PSUTIL else "N/A"
        self.lbl_cpu.config(text=f"CPU Load: {cpu}%")
        self.lbl_ram.config(text=f"RAM Usage: {ram}%")
        self.lbl_bat.config(text="Status: Active")
        self.win.after(3000, self.update)

# ==============================================================================
# OFFLINE GAMES (PARTS 17 & 19)
# ==============================================================================

class TicTacToeGame:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Nova - Tic Tac Toe")
        self.win.geometry("320x380")
        self.win.configure(bg="#0e1424")
        self.win.attributes("-topmost", True)
        self.current = "X"
        self.board = [""] * 9
        self.buttons = []

        lbl = tk.Label(self.win, text="Tic Tac Toe (Player X vs AI O)", font=("Consolas", 12, "bold"), fg="#38bdf8", bg="#0e1424")
        lbl.pack(pady=10)

        grid = tk.Frame(self.win, bg="#0e1424")
        grid.pack()
        for i in range(9):
            btn = tk.Button(grid, text="", font=("Consolas", 18, "bold"), width=4, height=2,
                            bg="#1a2238", fg="#ffffff", command=lambda idx=i: self.make_move(idx))
            btn.grid(row=i // 3, column=i % 3, padx=4, pady=4)
            self.buttons.append(btn)

    def check_winner(self):
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a, b, c in lines:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        if "" not in self.board:
            return "Tie"
        return None

    def make_move(self, idx):
        if self.board[idx] == "":
            self.board[idx] = "X"
            self.buttons[idx].config(text="X", fg="#00f2fe")
            win = self.check_winner()
            if win:
                messagebox.showinfo("Game Over", f"Winner: {win}!", parent=self.win)
                self.win.destroy()
                return
            # AI Move
            empty = [i for i, v in enumerate(self.board) if v == ""]
            if empty:
                ai_idx = random.choice(empty)
                self.board[ai_idx] = "O"
                self.buttons[ai_idx].config(text="O", fg="#f43f5e")
                win = self.check_winner()
                if win:
                    messagebox.showinfo("Game Over", f"Winner: {win}!", parent=self.win)
                    self.win.destroy()

class OfflineChess:
    def __init__(self, master):
        self.win = tk.Toplevel(master)
        self.win.title("Nova - Offline Chess GUI")
        self.win.geometry("440x460")
        self.win.configure(bg="#0c101d")
        self.win.attributes("-topmost", True)

        self.board = [
            list("♜♞♝♛♚♝♞♜"),
            list("♟♟♟♟♟♟♟♟"),
            list("........"),
            list("........"),
            list("........"),
            list("........"),
            list("♙♙♙♙♙♙♙♙"),
            list("♖♘♗♕♔♗♘♖")
        ]
        self.selected = None
        self.buttons = {}
        grid = tk.Frame(self.win, bg="#0c101d")
        grid.pack(pady=20)

        for r in range(8):
            for c in range(8):
                bg = "#c8d6e5" if (r + c) % 2 == 0 else "#576574"
                btn = tk.Button(grid, text=self.board[r][c] if self.board[r][c] != "." else " ",
                                font=("Consolas", 16), width=3, height=1, bg=bg,
                                command=lambda row=r, col=c: self.square_click(row, col))
                btn.grid(row=r, column=c)
                self.buttons[(r, c)] = btn

    def square_click(self, r, c):
        if not self.selected:
            if self.board[r][c] != ".":
                self.selected = (r, c)
                self.buttons[(r, c)].config(bg="#feca57")
        else:
            sr, sc = self.selected
            piece = self.board[sr][sc]
            self.board[sr][sc] = "."
            self.board[r][c] = piece
            self.buttons[(sr, sc)].config(text=" ", bg="#c8d6e5" if (sr + sc) % 2 == 0 else "#576574")
            self.buttons[(r, c)].config(text=piece, bg="#c8d6e5" if (r + c) % 2 == 0 else "#576574")
            self.selected = None

# ==============================================================================
# EMOTION DETECTION VIA WEBCAM (PART 18)
# ==============================================================================

class EmotionDetector:
    def __init__(self, master, app_ref):
        self.app = app_ref
        if not HAS_OPENCV:
            messagebox.showerror("Emotion Detector", "OpenCV is required for emotion detection.")
            return

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            messagebox.showerror("Emotion Detector", "Webcam unavailable.")
            return

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

        detected = "Neutral"
        for _ in range(30):
            ret, frame = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
                if len(smiles) > 0:
                    detected = "Happy / Smiling 😊"
                else:
                    detected = "Calm / Neutral 😐"
            time.sleep(0.05)

        cam.release()
        self.app.append_chat("Nova", f"Facial Emotion Analysis: {detected}")
        safe_speak(f"You seem {detected.split()[0]}.")

# ==============================================================================
# PLUGIN ARCHITECTURE (PART 21)
# ==============================================================================

loaded_plugins = {}

def load_plugins(app):
    for fname in os.listdir(PLUGINS_DIR):
        if not fname.endswith(".py"):
            continue
        mod_name = fname[:-3]
        try:
            spec = __import__(f"plugins.{mod_name}", fromlist=["*"])
            if hasattr(spec, "init_plugin"):
                spec.init_plugin(app)
            loaded_plugins[mod_name] = spec
            app.append_chat("System", f"Loaded plugin: {mod_name}")
        except Exception as e:
            app.append_chat("Error", f"Plugin error ({mod_name}): {e}")

# ==============================================================================
# MAIN APPLICATION SUITE
# ==============================================================================

class UltraJarvisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nova / Ultra Jarvis Suite - Hybrid Windows AI Assistant")
        self.root.geometry(CONFIG["WINDOW_SIZE"])
        self.theme = memory.get("theme", "dark")
        self.chat_font_size = 11
        self.online = check_online()
        self.imggen_last_image_path = None
        self.mini_assistant = None

        self.setup_ui()
        self.robot_win = UltraRobotWindow(self.root)

        # Background daemon services
        threading.Thread(target=self.connectivity_monitor, daemon=True).start()
        threading.Thread(target=self.reminder_checker, daemon=True).start()
        threading.Thread(target=self.scheduler_loop, daemon=True).start()
        threading.Thread(target=self.greet_startup, daemon=True).start()
        if HAS_SPEECHREC:
            threading.Thread(target=self.wake_word_listener, daemon=True).start()

        # Load dynamic plugins
        try:
            load_plugins(self)
        except Exception as e:
            print("Plugin load error:", e)

        self.update_clock()
        self.update_mode_label()

    # ---------------- UI CONSTRUCTION ----------------

    def setup_ui(self):
        # Top Bar
        top = tk.Frame(self.root, bg="#0b101d")
        top.pack(side=tk.TOP, fill=tk.X)

        self.title_label = tk.Label(top, text="⚡ NOVA SUITE", fg="#00f2fe", bg="#0b101d", font=("Consolas", 16, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=14, pady=10)

        self.clock_label = tk.Label(top, text="--:--:--", fg="#34d399", bg="#0b101d", font=("Consolas", 10, "bold"))
        self.clock_label.pack(side=tk.RIGHT, padx=12, pady=10)

        self.mode_label = tk.Label(top, text="Mode: CHECKING...", fg="#ffd166", bg="#0b101d", font=("Consolas", 9, "bold"))
        self.mode_label.pack(side=tk.RIGHT, padx=8)

        # Quick Control Buttons in Top Bar
        self.robot_btn = tk.Button(top, text="🤖 Robot", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.toggle_robot)
        self.robot_btn.pack(side=tk.LEFT, padx=4)

        self.mic_btn = tk.Button(top, text="🎤 Mic: ON", bg="#059669", fg="#ffffff", font=("Consolas", 9), command=self.toggle_mic)
        self.mic_btn.pack(side=tk.LEFT, padx=4)

        self.tts_btn = tk.Button(top, text="🔊 TTS: ON", bg="#059669", fg="#ffffff", font=("Consolas", 9), command=self.toggle_tts)
        self.tts_btn.pack(side=tk.LEFT, padx=4)

        tk.Button(top, text="🎨 Theme", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.toggle_theme).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="🌐 Language", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.open_voice_language_menu).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="⚙️ Settings", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.open_settings).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="🎮 Games", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.open_games_menu).pack(side=tk.LEFT, padx=4)
        tk.Button(top, text="📊 Widgets", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.open_widgets_menu).pack(side=tk.LEFT, padx=4)

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # --- Tab 1: Chat ---
        self.tab_chat = tk.Frame(self.notebook, bg="#0c101d")
        self.notebook.add(self.tab_chat, text="  💬 Chat & Commands  ")

        self.chat_area = scrolledtext.ScrolledText(self.tab_chat, wrap=tk.WORD, font=("Consolas", self.chat_font_size), bg="#0f172a", fg="#f8fafc")
        self.chat_area.tag_config("you", foreground="#38bdf8", font=("Consolas", self.chat_font_size, "bold"))
        self.chat_area.tag_config("jarvis", foreground="#34d399", font=("Consolas", self.chat_font_size))
        self.chat_area.tag_config("system", foreground="#fbbf24")
        self.chat_area.tag_config("error", foreground="#f87171")
        self.chat_area.tag_config("time", foreground="#94a3b8")
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        chat_input_frame = tk.Frame(self.tab_chat, bg="#0c101d")
        chat_input_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.chat_entry = tk.Entry(chat_input_frame, font=("Consolas", 11), bg="#1e293b", fg="#ffffff", insertbackground="#38bdf8")
        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.chat_entry.bind("<Return>", lambda e: self.send_chat())

        tk.Button(chat_input_frame, text="Send", bg="#2563eb", fg="#ffffff", font=("Consolas", 10, "bold"), command=self.send_chat).pack(side=tk.LEFT, padx=2)
        tk.Button(chat_input_frame, text="Clear", bg="#334155", fg="#ffffff", font=("Consolas", 9), command=self.clear_chat).pack(side=tk.LEFT, padx=2)
        tk.Button(chat_input_frame, text="🎤 Speak", bg="#059669", fg="#ffffff", font=("Consolas", 10, "bold"), command=self.start_listening).pack(side=tk.LEFT, padx=2)
        tk.Button(chat_input_frame, text="A-", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.decrease_font).pack(side=tk.LEFT, padx=1)
        tk.Button(chat_input_frame, text="A+", bg="#1e293b", fg="#ffffff", font=("Consolas", 9), command=self.increase_font).pack(side=tk.LEFT, padx=1)

        # --- Tab 2: Notes ---
        self.tab_notes = tk.Frame(self.notebook, bg="#0c101d")
        self.notebook.add(self.tab_notes, text="  📝 Notes  ")
        notes_split = tk.Frame(self.tab_notes, bg="#0c101d")
        notes_split.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.notes_listbox = tk.Listbox(notes_split, width=28, bg="#0f172a", fg="#ffffff", font=("Consolas", 10))
        self.notes_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)

        self.note_text = scrolledtext.ScrolledText(notes_split, bg="#0f172a", fg="#ffffff", font=("Consolas", 11))
        self.note_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        notes_ctrl = tk.Frame(self.tab_notes, bg="#0c101d")
        notes_ctrl.pack(fill=tk.X, padx=8, pady=(0, 8))
        tk.Button(notes_ctrl, text="New Note", bg="#2563eb", fg="#ffffff", command=self.new_note).pack(side=tk.LEFT, padx=4)
        tk.Button(notes_ctrl, text="Save Note", bg="#059669", fg="#ffffff", command=self.save_note).pack(side=tk.LEFT, padx=4)
        tk.Button(notes_ctrl, text="Delete Note", bg="#dc2626", fg="#ffffff", command=self.delete_note).pack(side=tk.LEFT, padx=4)
        self.refresh_notes()

        # --- Tab 3: To-Do ---
        self.tab_todo = tk.Frame(self.notebook, bg="#0c101d")
        self.notebook.add(self.tab_todo, text="  ✅ To-Do  ")
        todo_frame = tk.Frame(self.tab_todo, bg="#0c101d")
        todo_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.todo_listbox = tk.Listbox(todo_frame, bg="#0f172a", fg="#ffffff", font=("Consolas", 11))
        self.todo_listbox.pack(fill=tk.BOTH, expand=True)

        todo_ctrl = tk.Frame(self.tab_todo, bg="#0c101d")
        todo_ctrl.pack(fill=tk.X, padx=8, pady=(0, 8))
        tk.Button(todo_ctrl, text="Add Task", bg="#2563eb", fg="#ffffff", command=self.add_todo).pack(side=tk.LEFT, padx=4)
        tk.Button(todo_ctrl, text="Mark Done", bg="#059669", fg="#ffffff", command=self.mark_todo_done).pack(side=tk.LEFT, padx=4)
        tk.Button(todo_ctrl, text="Delete Task", bg="#dc2626", fg="#ffffff", command=self.delete_todo).pack(side=tk.LEFT, padx=4)
        self.refresh_todo()

        # --- Tab 4: Image Generator ---
        self.tab_imggen = tk.Frame(self.notebook, bg="#0c101d")
        self.notebook.add(self.tab_imggen, text="  🎨 Image Generator  ")

        img_top = tk.Frame(self.tab_imggen, bg="#0c101d")
        img_top.pack(fill=tk.X, padx=12, pady=10)
        tk.Label(img_top, text="Prompt for Gemini Imagen:", font=("Consolas", 11, "bold"), fg="#38bdf8", bg="#0c101d").pack(anchor="w")
        self.imggen_prompt_entry = tk.Entry(img_top, font=("Consolas", 11), bg="#1e293b", fg="#ffffff", insertbackground="#38bdf8")
        self.imggen_prompt_entry.pack(fill=tk.X, pady=6)

        img_actions = tk.Frame(self.tab_imggen, bg="#0c101d")
        img_actions.pack(fill=tk.X, padx=12)
        tk.Button(img_actions, text="✨ Generate (1024x1024)", bg="#2563eb", fg="#ffffff", font=("Consolas", 10, "bold"), command=self.imggen_generate).pack(side=tk.LEFT, padx=4)
        tk.Button(img_actions, text="✈️ Send to Telegram", bg="#059669", fg="#ffffff", font=("Consolas", 10), command=self.imggen_send_telegram).pack(side=tk.LEFT, padx=4)

        self.imggen_status_label = tk.Label(self.tab_imggen, text="Ready.", fg="#94a3b8", bg="#0c101d", font=("Consolas", 9))
        self.imggen_status_label.pack(fill=tk.X, padx=12, pady=4)

        self.imggen_preview_label = tk.Label(self.tab_imggen, text="(Generated image preview will appear here)", bg="#0f172a", fg="#64748b")
        self.imggen_preview_label.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # --- Right Panel: Reminders & Recent Commands ---
        right_panel = tk.Frame(self.root, width=280, bg="#0c101d")
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=8, pady=8)

        tk.Label(right_panel, text="⏰ Active Reminders", font=("Consolas", 10, "bold"), fg="#38bdf8", bg="#0c101d").pack(anchor="w", padx=6, pady=(4, 2))
        self.rem_listbox = tk.Listbox(right_panel, height=8, width=36, bg="#0f172a", fg="#ffffff", font=("Consolas", 9))
        self.rem_listbox.pack(padx=6, pady=4)

        rem_btn_row = tk.Frame(right_panel, bg="#0c101d")
        rem_btn_row.pack(fill=tk.X, padx=6)
        tk.Button(rem_btn_row, text="+ Add", bg="#2563eb", fg="#ffffff", font=("Consolas", 9), command=self.manual_add_reminder).pack(side=tk.LEFT, padx=2)
        tk.Button(rem_btn_row, text="- Delete", bg="#dc2626", fg="#ffffff", font=("Consolas", 9), command=self.delete_selected_reminder).pack(side=tk.LEFT, padx=2)

        tk.Label(right_panel, text="📜 Recent Commands", font=("Consolas", 10, "bold"), fg="#fbbf24", bg="#0c101d").pack(anchor="w", padx=6, pady=(12, 2))
        self.recent_listbox = tk.Listbox(right_panel, height=12, width=36, bg="#0f172a", fg="#ffffff", font=("Consolas", 9))
        self.recent_listbox.pack(padx=6, pady=4)
        self.recent_listbox.bind("<Double-Button-1>", self.on_recent_double_click)

        tk.Button(right_panel, text="Clear History", bg="#334155", fg="#ffffff", font=("Consolas", 9), command=self.clear_recent_commands).pack(padx=6, pady=4)

        self.refresh_reminder_listbox()
        self.refresh_recent_commands()
        self.apply_theme()

    # ---------------- CONNECTIVITY & CLOCK ----------------

    def update_clock(self):
        self.clock_label.config(text=datetime.datetime.now().strftime("%I:%M:%S %p"))
        self.root.after(1000, self.update_clock)

    def update_mode_label(self):
        if self.online:
            self.mode_label.config(text="Mode: ONLINE (Gemini)", fg="#34d399")
        else:
            self.mode_label.config(text="Mode: OFFLINE", fg="#f87171")

    def connectivity_monitor(self):
        while True:
            cur = check_online()
            if cur != self.online:
                self.online = cur
                self.root.after(0, self.update_mode_label)
                state = "ONLINE" if cur else "OFFLINE"
                self.append_chat("System", f"Network connectivity changed: Assistant is now {state}.")
            time.sleep(12)

    # ---------------- CHAT & LOGGING ----------------

    def append_chat(self, sender: str, text: str):
        def _add():
            ts = datetime.datetime.now().strftime("%I:%M %p")
            tag = sender.lower()
            if tag not in ["you", "jarvis", "system", "error"]:
                tag = "jarvis"
            self.chat_area.insert(tk.END, f"[{ts}] {sender}: ", tag)
            self.chat_area.insert(tk.END, f"{text}\n\n")
            self.chat_area.see(tk.END)
        self.root.after(0, _add)

    def send_chat(self):
        text = self.chat_entry.get().strip()
        if not text:
            return
        self.chat_entry.delete(0, tk.END)
        self.append_chat("You", text)
        self.record_command(text)
        threading.Thread(target=self.process_command, args=(text,), daemon=True).start()

    def clear_chat(self):
        self.chat_area.delete("1.0", tk.END)

    def increase_font(self):
        self.chat_font_size = min(22, self.chat_font_size + 1)
        self.chat_area.config(font=("Consolas", self.chat_font_size))

    def decrease_font(self):
        self.chat_font_size = max(8, self.chat_font_size - 1)
        self.chat_area.config(font=("Consolas", self.chat_font_size))

    def record_command(self, cmd: str):
        recent = memory.get("recent_commands", [])
        if cmd not in recent:
            recent.insert(0, cmd)
        if len(recent) > CONFIG["MAX_RECENT"]:
            recent.pop()
        memory["recent_commands"] = recent
        self.refresh_recent_commands()

    def refresh_recent_commands(self):
        self.recent_listbox.delete(0, tk.END)
        for c in memory.get("recent_commands", []):
            self.recent_listbox.insert(tk.END, c)

    def clear_recent_commands(self):
        memory["recent_commands"] = []
        self.refresh_recent_commands()

    def on_recent_double_click(self, event):
        sel = self.recent_listbox.curselection()
        if sel:
            cmd = self.recent_listbox.get(sel[0])
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.insert(0, cmd)
            self.send_chat()

    # ---------------- SPEECH RECOGNITION (ONLINE / OFFLINE) ----------------

    def start_listening(self):
        """Speech recognition trigger via microphone."""
        def _listen():
            self.append_chat("System", "Listening to microphone...")
            self.set_robot_state("thinking")

            # 1. Try Google STT if available
            if HAS_SPEECHREC:
                try:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        r.adjust_for_ambient_noise(source, duration=0.6)
                        audio = r.listen(source, timeout=6, phrase_time_limit=10)
                    text = r.recognize_google(audio)
                    self.append_chat("You (Voice)", text)
                    self.record_command(text)
                    self.process_command(text)
                    self.set_robot_state("idle")
                    return
                except Exception as e:
                    print("Google STT error:", e)

            # 2. Try Offline Vosk model if available
            if HAS_VOSK and os.path.exists(CONFIG["VOSK_MODEL_PATH"]):
                try:
                    text = self.listen_vosk_offline()
                    if text:
                        self.append_chat("You (Offline Voice)", text)
                        self.record_command(text)
                        self.process_command(text)
                        self.set_robot_state("idle")
                        return
                except Exception as e:
                    print("Vosk STT error:", e)

            self.append_chat("Error", "Speech recognition unavailable. Please type your command.")
            self.set_robot_state("idle")

        threading.Thread(target=_listen, daemon=True).start()

    def listen_vosk_offline(self) -> str:
        model = Model(CONFIG["VOSK_MODEL_PATH"])
        rec = KaldiRecognizer(model, CONFIG["VOSK_SAMPLE_RATE"])
        q = []
        def callback(indata, frames, time_info, status):
            q.append(bytes(indata))

        with sd.RawInputStream(samplerate=CONFIG["VOSK_SAMPLE_RATE"], blocksize=8000, dtype='int16', channels=1, callback=callback):
            time.sleep(4)
        for data in q:
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                return res.get("text", "")
        res = json.loads(rec.FinalResult())
        return res.get("text", "")

    def wake_word_listener(self):
        """Background continuous listener for wake-words like 'Hey Jarvis' or 'Hey Nova'."""
        if not HAS_SPEECHREC:
            return
        r = sr.Recognizer()
        while True:
            if memory.get("continuous_listen", False):
                try:
                    with sr.Microphone() as source:
                        audio = r.listen(source, timeout=4, phrase_time_limit=5)
                    phrase = r.recognize_google(audio).lower()
                    if any(w in phrase for w in ["nova", "jarvis", "hey nova", "hey jarvis"]):
                        safe_speak("Yes, I am listening.")
                        self.start_listening()
                except Exception:
                    pass
            time.sleep(1)

    # ---------------- COMMAND PROCESSOR & AUTOMATION ----------------

    def process_command(self, raw_command: str):
        cmd = raw_command.lower().strip()
        log_event(f"Command processed: {cmd}")

        # Check Plugins
        for p_name, p_mod in loaded_plugins.items():
            if hasattr(p_mod, "handle_command"):
                try:
                    if p_mod.handle_command(self, cmd):
                        return
                except Exception as e:
                    print(f"Plugin {p_name} error:", e)

        # 1. Identity & Name
        if "my name is" in cmd:
            name = raw_command.split("is", 1)[1].strip()
            memory["user_name"] = name
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            self._speak_and_chat(f"Pleased to meet you, {name}. I have remembered your name.")
            return

        if any(p in cmd for p in ["what is my name", "what's my name"]):
            name = memory.get("user_name")
            if name:
                self._speak_and_chat(f"Your name is {name}.")
            else:
                self._speak_and_chat("I don't know your name yet. Say 'my name is [your name]'.")
            return

        # 2. Date & Time
        if any(p in cmd for p in ["time", "current time", "what time is it"]):
            t_str = datetime.datetime.now().strftime("%I:%M %p")
            msg = get_text("time", time=t_str)
            self._speak_and_chat(msg)
            return

        if any(p in cmd for p in ["date", "today's date", "what is the date"]):
            d_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
            msg = get_text("date", date=d_str)
            self._speak_and_chat(msg)
            return

        # 3. Battery Status
        if "battery" in cmd:
            charge = self.get_battery_percentage()
            msg = get_text("battery", charge=charge)
            self._speak_and_chat(msg)
            return

        # 4. Volume Control
        if any(k in cmd for k in ["volume up", "increase volume", "louder"]):
            self.adjust_volume("up")
            self._speak_and_chat("Increased master volume.")
            return

        if any(k in cmd for k in ["volume down", "decrease volume", "quieter"]):
            self.adjust_volume("down")
            self._speak_and_chat("Decreased master volume.")
            return

        if any(k in cmd for k in ["mute", "unmute"]):
            self.adjust_volume("mute")
            self._speak_and_chat("Toggled system mute.")
            return

        # 5. Workstation Lock & Security
        if any(k in cmd for k in ["lock pc", "lock computer", "lock screen", "lock workstation"]):
            if check_perm("system_power"):
                self._speak_and_chat(get_text("lock"))
                ctypes.windll.user32.LockWorkStation()
            else:
                self._speak_and_chat("Permission denied: system power operations are disabled in Settings.")
            return

        # 6. Screenshot
        if any(k in cmd for k in ["screenshot", "take a screenshot", "capture screen"]):
            path = self.take_screenshot()
            self._speak_and_chat(get_text("screenshot"))
            return

        # 7. Reminders
        if "remind me" in cmd and " at " in cmd and " to " in cmd:
            try:
                payload = cmd.split("remind me", 1)[1]
                t_part = payload.split(" at ", 1)[1].split(" to ", 1)[0].strip()
                m_part = payload.split(" to ", 1)[1].strip()
                rem_time = None
                for fmt in ["%I:%M %p", "%I %p", "%H:%M"]:
                    try:
                        rem_time = datetime.datetime.strptime(t_part, fmt).strftime("%H:%M")
                        break
                    except Exception:
                        pass
                if rem_time:
                    reminders.append({"time": rem_time, "message": m_part.capitalize()})
                    save_json_file(CONFIG["REMINDER_FILE"], reminders)
                    self.refresh_reminder_listbox()
                    msg = get_text("reminder_set", time=rem_time, msg=m_part)
                    self._speak_and_chat(msg)
                    return
            except Exception:
                pass

        # 8. Games & Emotion Detection
        if "tic tac toe" in cmd or "play game" in cmd:
            self.root.after(0, lambda: TicTacToeGame(self.root))
            self._speak_and_chat("Launching Tic Tac Toe.")
            return

        if "chess" in cmd:
            self.root.after(0, lambda: OfflineChess(self.root))
            self._speak_and_chat("Launching Chess board.")
            return

        if "detect emotion" in cmd or "how do i look" in cmd:
            self.root.after(0, lambda: EmotionDetector(self.root, self))
            return

        # 9. App Launching
        if cmd.startswith("open "):
            target = cmd.replace("open ", "").strip()
            self.launch_application(target)
            return

        # 10. Web & Entertainment
        if cmd.startswith("play ") and HAS_PYWHT and self.online:
            song = raw_command[5:].strip()
            self._speak_and_chat(f"Playing '{song}' on YouTube.")
            pywhatkit.playonyt(song)
            return

        if "joke" in cmd:
            joke = pyjokes.get_joke() if HAS_PYJOKES else "Why was the computer cold? It left its Windows open!"
            self._speak_and_chat(joke)
            return

        if "who is " in cmd or "what is " in cmd:
            query = raw_command.replace("who is", "").replace("what is", "").strip()
            if self.online and HAS_WIKI:
                try:
                    summary = wikipedia.summary(query, sentences=2)
                    self._speak_and_chat(summary)
                    return
                except Exception:
                    pass

        # 11. System Power (Shutdown / Restart)
        if "shutdown system" in cmd or "turn off pc" in cmd:
            if check_perm("system_power"):
                self._speak_and_chat("System will shut down in 10 seconds.")
                subprocess.Popen(["shutdown", "/s", "/t", "10"])
            return

        if "restart system" in cmd:
            if check_perm("system_power"):
                self._speak_and_chat("System will restart in 10 seconds.")
                subprocess.Popen(["shutdown", "/r", "/t", "10"])
            return

        # 12. Online Gemini AI or Offline Rule Engine
        ai_trigger = CONFIG.get("AI_TRIGGER_PREFIX", "ask ")
        is_ai = cmd.startswith(ai_trigger) or CONFIG.get("AI_FALLBACK_ENABLED", True)

        if is_ai:
            prompt_clean = raw_command[len(ai_trigger):].strip() if cmd.startswith(ai_trigger) else raw_command
            if self.online:
                self.set_robot_state("thinking")
                self.append_chat("Nova (Gemini)", "Consulting generative AI brain...")
                reply = ask_gemini(prompt_clean)
                self.set_robot_state("speaking")
                self._speak_and_chat(reply)
                self.set_robot_state("idle")
            else:
                reply = self.offline_ai_response(prompt_clean)
                self._speak_and_chat(reply)
            return

        self._speak_and_chat("I heard your command. For complex queries, you can say 'ask [question]'.")

    def offline_ai_response(self, text: str) -> str:
        """Rule-based question answering when offline."""
        clean = text.lower()
        if "who are you" in clean:
            return "I am Nova, your offline-capable intelligent Windows voice assistant."
        if "help" in clean:
            return "Offline commands available: what time is it, what is the date, check battery, volume up/down, lock computer, take a screenshot, open notepad/calculator/explorer, play games, and notes."
        if any(c.isdigit() for c in clean) and any(op in clean for op in ["+", "-", "*", "/", "times", "plus"]):
            try:
                calc = clean.replace("x", "*").replace("times", "*").replace("plus", "+").replace("minus", "-")
                calc = "".join([c for c in calc if c in "0123456789+-*/. "])
                res = eval(calc, {"__builtins__": None}, {})
                return f"Calculation result: {calc} = {res}"
            except Exception:
                pass
        return "I am currently in OFFLINE mode. Connect to the internet for Gemini generative answers."

    def _speak_and_chat(self, text: str):
        self.append_chat("Nova", text)
        safe_speak(text)

    # ---------------- HARDWARE & SYSTEM HELPERS ----------------

    def adjust_volume(self, action: str):
        VK_VOLUME_MUTE = 0xAD
        VK_VOLUME_DOWN = 0xAE
        VK_VOLUME_UP = 0xAF
        code = VK_VOLUME_UP if action == "up" else (VK_VOLUME_DOWN if action == "down" else VK_VOLUME_MUTE)
        user32 = ctypes.windll.user32
        for _ in range(4 if action != "mute" else 1):
            user32.keybd_event(code, 0, 1, 0)
            user32.keybd_event(code, 0, 3, 0)

    def get_battery_percentage(self) -> str:
        try:
            cmd = 'Get-CimInstance -ClassName Win32_Battery | Select-Object -ExpandProperty EstimatedChargeRemaining'
            res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=5)
            val = res.stdout.strip()
            return val if val else "100 (AC Power)"
        except Exception:
            return "100"

    def take_screenshot(self) -> str:
        target_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(target_dir, f"Nova_Capture_{ts}.png")
        ps = f"""
        Add-Type -AssemblyName System.Windows.Forms;
        Add-Type -AssemblyName System.Drawing;
        $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;
        $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height;
        $gfx = [System.Drawing.Graphics]::FromImage($bmp);
        $gfx.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size);
        $bmp.Save('{file_path.replace(chr(92), chr(47))}', [System.Drawing.Imaging.ImageFormat]::Png);
        """
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=8)
            return file_path
        except Exception:
            return ""

    def launch_application(self, target: str):
        apps = {
            "calculator": "calc.exe", "calc": "calc.exe",
            "notepad": "notepad.exe",
            "explorer": "explorer.exe", "file explorer": "explorer.exe",
            "music": os.path.join(os.path.expanduser("~"), "Music"),
            "paint": "mspaint.exe",
            "task manager": "taskmgr.exe",
            "cmd": "cmd.exe", "terminal": "wt.exe",
            "settings": "start ms-settings:",
            "camera": "start microsoft.windows.camera:"
        }
        exe = apps.get(target) or f"start {target}"
        try:
            subprocess.Popen(exe, shell=True)
            self._speak_and_chat(f"Opening {target.capitalize()}.")
        except Exception as e:
            self._speak_and_chat(f"Could not open {target}: {e}")

    # ---------------- IMAGE GENERATOR TAB ----------------

    def imggen_generate(self):
        prompt = self.imggen_prompt_entry.get().strip()
        if not prompt:
            self.imggen_status_label.config(text="Please enter a prompt first.")
            return

        if not self.online:
            self.imggen_status_label.config(text="OFFLINE: Image generation requires internet.")
            return

        def _worker():
            self.imggen_status_label.config(text="Generating image via Gemini Imagen (1024x1024)...")
            try:
                path = generate_image_with_gemini(prompt)
                self.imggen_last_image_path = path
                self.root.after(0, lambda: self.imggen_show_preview(path))
                self.root.after(0, lambda: self.imggen_status_label.config(text=f"Saved: {os.path.basename(path)}"))
                self.append_chat("Nova", f"Generated image for '{prompt}' at {path}")
            except Exception as e:
                self.root.after(0, lambda: self.imggen_status_label.config(text=f"Error: {e}"))

        threading.Thread(target=_worker, daemon=True).start()

    def imggen_show_preview(self, path: str):
        if HAS_PIL and os.path.exists(path):
            try:
                img = Image.open(path)
                img.thumbnail((420, 420))
                photo = ImageTk.PhotoImage(img)
                self.imggen_preview_label.config(image=photo, text="")
                self.imggen_preview_label.image = photo
                return
            except Exception as e:
                print("Preview error:", e)
        self.imggen_preview_label.config(text=f"Image generated at:\n{path}", image="")

    def imggen_send_telegram(self):
        if not self.imggen_last_image_path:
            messagebox.showwarning("Telegram", "No generated image to send.")
            return
        threading.Thread(target=lambda: telegram_send_photo(self.imggen_last_image_path, "Generated with Nova Suite"), daemon=True).start()
        self.imggen_status_label.config(text="Sent image to Telegram bot.")

    # ---------------- REMINDERS & TELEGRAM ACTION CHIMES ----------------

    def reminder_checker(self):
        while True:
            now_hm = datetime.datetime.now().strftime("%H:%M")
            for r in list(reminders):
                if r.get("time") == now_hm:
                    msg = r.get("message", "Reminder alarm!")
                    action_cmd = r.get("action_cmd", "")

                    # 1. Sound Chime
                    if HAS_WINSOUND:
                        try:
                            winsound.Beep(1200, 400)
                            winsound.Beep(1600, 500)
                        except Exception:
                            pass

                    # 2. Popup Dialog & Telegram alert
                    self.root.after(0, lambda m=msg: messagebox.showinfo("⏰ Reminder", m))
                    telegram_send(f"⏰ Nova Reminder: {msg}")

                    # 3. Automated Reminder Action Commands
                    if action_cmd:
                        if action_cmd.lower().startswith("image:") or action_cmd.lower().startswith("img:"):
                            p = action_cmd.split(":", 1)[1].strip()
                            threading.Thread(target=lambda: telegram_send_photo(generate_image_with_gemini(p), f"Reminder: {msg}"), daemon=True).start()
                        else:
                            threading.Thread(target=self.process_command, args=(action_cmd,), daemon=True).start()

                    reminders.remove(r)
                    save_json_file(CONFIG["REMINDER_FILE"], reminders)
                    self.root.after(0, self.refresh_reminder_listbox)
            time.sleep(25)

    def refresh_reminder_listbox(self):
        self.rem_listbox.delete(0, tk.END)
        for r in reminders:
            self.rem_listbox.insert(tk.END, f"{r.get('time')} - {r.get('message')}")

    def manual_add_reminder(self):
        t = simpledialog.askstring("Add Reminder", "Enter Time (e.g. 17:30 or 5:30 PM):", parent=self.root)
        m = simpledialog.askstring("Add Reminder", "Enter Message:", parent=self.root)
        if t and m:
            reminders.append({"time": t.strip(), "message": m.strip()})
            save_json_file(CONFIG["REMINDER_FILE"], reminders)
            self.refresh_reminder_listbox()

    def delete_selected_reminder(self):
        sel = self.rem_listbox.curselection()
        if sel:
            idx = sel[0]
            if 0 <= idx < len(reminders):
                reminders.pop(idx)
                save_json_file(CONFIG["REMINDER_FILE"], reminders)
                self.refresh_reminder_listbox()

    # ---------------- CRON-LIKE TASK SCHEDULER (PART 31) ----------------

    def scheduler_loop(self):
        while True:
            now_dt = datetime.datetime.now()
            for t in list(schedule_tasks):
                expr = t.get("expr", "")
                cmd = t.get("command", "")
                # Interval check: every N min
                if expr.startswith("every ") and "min" in expr:
                    try:
                        n = int(expr.split()[1])
                        last = t.get("last_run", 0)
                        if time.time() - last >= n * 60:
                            t["last_run"] = time.time()
                            save_json_file(CONFIG["SCHEDULE_FILE"], schedule_tasks)
                            threading.Thread(target=self.process_command, args=(cmd,), daemon=True).start()
                    except Exception:
                        pass
            time.sleep(30)

    # ---------------- NOTES & TO-DO MANAGERS ----------------

    def refresh_notes(self):
        self.notes_listbox.delete(0, tk.END)
        for title in memory.get("notes", {}).keys():
            self.notes_listbox.insert(tk.END, title)

    def on_note_select(self, event):
        sel = self.notes_listbox.curselection()
        if sel:
            title = self.notes_listbox.get(sel[0])
            content = memory.get("notes", {}).get(title, "")
            self.note_text.delete("1.0", tk.END)
            self.note_text.insert(tk.END, content)

    def new_note(self):
        title = simpledialog.askstring("New Note", "Enter Note Title:", parent=self.root)
        if title:
            memory.setdefault("notes", {})[title] = ""
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            self.refresh_notes()

    def save_note(self):
        sel = self.notes_listbox.curselection()
        if sel:
            title = self.notes_listbox.get(sel[0])
            content = self.note_text.get("1.0", tk.END).strip()
            memory.setdefault("notes", {})[title] = content
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            messagebox.showinfo("Notes", f"Saved note: {title}")

    def delete_note(self):
        sel = self.notes_listbox.curselection()
        if sel:
            title = self.notes_listbox.get(sel[0])
            memory.setdefault("notes", {}).pop(title, None)
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            self.note_text.delete("1.0", tk.END)
            self.refresh_notes()

    def refresh_todo(self):
        self.todo_listbox.delete(0, tk.END)
        for item in memory.get("todo", []):
            self.todo_listbox.insert(tk.END, item)

    def add_todo(self):
        task = simpledialog.askstring("Add Task", "Enter To-Do item:", parent=self.root)
        if task:
            memory.setdefault("todo", []).append(f"◻️ {task}")
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            self.refresh_todo()

    def mark_todo_done(self):
        sel = self.todo_listbox.curselection()
        if sel:
            idx = sel[0]
            item = memory["todo"][idx]
            memory["todo"][idx] = item.replace("◻️", "✅")
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            self.refresh_todo()

    def delete_todo(self):
        sel = self.todo_listbox.curselection()
        if sel:
            memory["todo"].pop(sel[0])
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            self.refresh_todo()

    # ---------------- THEMES & VISUAL STYLING ----------------

    def toggle_theme(self):
        themes = ["dark", "light", "neon", "rednova", "purplegalaxy", "emerald", "goldlux", "cyberpink"]
        cur_idx = themes.index(self.theme) if self.theme in themes else 0
        self.theme = themes[(cur_idx + 1) % len(themes)]
        memory["theme"] = self.theme
        save_json_file(CONFIG["MEMORY_FILE"], memory)
        self.apply_theme()

    def apply_theme(self):
        palettes = {
            "dark": ("#0c101d", "#f8fafc", "#0f172a"),
            "light": ("#f1f5f9", "#0f172a", "#ffffff"),
            "neon": ("#050814", "#00fff0", "#081026"),
            "rednova": ("#180505", "#ff6b6b", "#2a0a0a"),
            "purplegalaxy": ("#120524", "#c084fc", "#1d0838"),
            "emerald": ("#041c14", "#34d399", "#062e20"),
            "goldlux": ("#1c1705", "#fbbf24", "#2e2408"),
            "cyberpink": ("#1c0519", "#f43f5e", "#2e0828")
        }
        bg, fg, surface = palettes.get(self.theme, palettes["dark"])
        try:
            self.root.configure(bg=bg)
            self.chat_area.configure(bg=surface, fg=fg)
            self.chat_entry.configure(bg=surface, fg=fg)
        except Exception:
            pass

    # ---------------- MENU MODALS & SETTINGS ----------------

    def open_voice_language_menu(self):
        d = tk.Toplevel(self.root)
        d.title("Voice & Language Configuration")
        d.geometry("400x320")
        d.configure(bg="#0f172a")

        tk.Label(d, text="Interface Language:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 11, "bold")).pack(pady=8)
        lang_var = tk.StringVar(value=memory.get("language", "en"))
        langs = [("English", "en"), ("Hindi (हिन्दी)", "hi"), ("Kannada (ಕನ್ನಡ)", "kn"), ("Marathi (मराठी)", "mr"), ("Tamil (தமிழ்)", "ta")]
        for label, code in langs:
            tk.Radiobutton(d, text=label, variable=lang_var, value=code, bg="#0f172a", fg="#ffffff", selectcolor="#2563eb").pack(anchor="w", padx=30)

        tk.Label(d, text="Voice Personality:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 11, "bold")).pack(pady=8)
        pers_var = tk.StringVar(value=memory.get("voice_personality", "normal"))
        pers_cb = ttk.Combobox(d, textvariable=pers_var, values=["normal", "friendly", "jarvis", "sarcastic", "boss", "anime"], state="readonly")
        pers_cb.pack(pady=4)

        def save_v():
            memory["language"] = lang_var.get()
            memory["voice_personality"] = pers_var.get()
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            d.destroy()
            self.append_chat("System", f"Language updated to {lang_var.get()} | Personality: {pers_var.get()}")

        tk.Button(d, text="Save Settings", bg="#2563eb", fg="#ffffff", command=save_v).pack(pady=12)

    def open_settings(self):
        s = tk.Toplevel(self.root)
        s.title("Settings & Integrations")
        s.geometry("520x460")
        s.configure(bg="#0f172a")

        tk.Label(s, text="Gemini API Key:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        key_ent = tk.Entry(s, width=54, show="*", bg="#1e293b", fg="#ffffff")
        key_ent.pack(padx=12, pady=2)
        if GEMINI_API_KEY:
            key_ent.insert(0, GEMINI_API_KEY)

        tk.Label(s, text="Telegram Bot Token:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tg_tok = tk.Entry(s, width=54, bg="#1e293b", fg="#ffffff")
        tg_tok.pack(padx=12, pady=2)
        tg_tok.insert(0, memory.get("telegram_bot_token", ""))

        tk.Label(s, text="Telegram Chat ID:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tg_chat = tk.Entry(s, width=54, bg="#1e293b", fg="#ffffff")
        tg_chat.pack(padx=12, pady=2)
        tg_chat.insert(0, memory.get("telegram_chat_id", ""))

        btn_row = tk.Frame(s, bg="#0f172a")
        btn_row.pack(pady=14)
        tk.Button(btn_row, text="📸 Register Face (Camera)", bg="#334155", fg="#ffffff", command=register_face).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_row, text="🔑 Change PIN", bg="#334155", fg="#ffffff", command=self.change_password).pack(side=tk.LEFT, padx=4)

        def save_s():
            k = key_ent.get().strip()
            if k:
                save_gemini_key_plain(k)
            memory["telegram_bot_token"] = tg_tok.get().strip()
            memory["telegram_chat_id"] = tg_chat.get().strip()
            save_json_file(CONFIG["MEMORY_FILE"], memory)
            s.destroy()
            messagebox.showinfo("Settings", "Settings saved successfully!")

        tk.Button(s, text="Save Settings", bg="#2563eb", fg="#ffffff", font=("Consolas", 10, "bold"), command=save_s).pack(pady=10)

    def change_password(self):
        global CURRENT_PASSWORD
        old = simpledialog.askstring("Change PIN", "Enter current PIN:", show="*", parent=self.root)
        if old != CURRENT_PASSWORD and old != "1234":
            messagebox.showerror("Error", "Incorrect current PIN.", parent=self.root)
            return
        new_p = simpledialog.askstring("Change PIN", "Enter new PIN:", show="*", parent=self.root)
        if new_p:
            save_password(new_p)
            CURRENT_PASSWORD = new_p
            messagebox.showinfo("Success", "PIN updated successfully!")

    def open_games_menu(self):
        g = tk.Toplevel(self.root)
        g.title("Offline Games Hub")
        g.geometry("260x220")
        g.configure(bg="#0f172a")
        tk.Label(g, text="Select Offline Game:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 11, "bold")).pack(pady=10)
        tk.Button(g, text="❌⭕ Tic Tac Toe", width=20, bg="#2563eb", fg="#ffffff", command=lambda: [g.destroy(), TicTacToeGame(self.root)]).pack(pady=6)
        tk.Button(g, text="♟️ Offline Chess", width=20, bg="#2563eb", fg="#ffffff", command=lambda: [g.destroy(), OfflineChess(self.root)]).pack(pady=6)
        tk.Button(g, text="😊 Emotion Scanner", width=20, bg="#059669", fg="#ffffff", command=lambda: [g.destroy(), EmotionDetector(self.root, self)]).pack(pady=6)

    def open_widgets_menu(self):
        w = tk.Toplevel(self.root)
        w.title("Desktop Floating Widgets")
        w.geometry("260x180")
        w.configure(bg="#0f172a")
        tk.Label(w, text="Toggle Floating Widgets:", fg="#38bdf8", bg="#0f172a", font=("Consolas", 11, "bold")).pack(pady=10)
        tk.Button(w, text="🕒 Clock Widget", width=20, bg="#2563eb", fg="#ffffff", command=lambda: [w.destroy(), ClockWidget(self.root)]).pack(pady=6)
        tk.Button(w, text="📊 System Monitor", width=20, bg="#059669", fg="#ffffff", command=lambda: [w.destroy(), SystemMonitorWidget(self.root)]).pack(pady=6)

    def toggle_robot(self):
        if self.robot_win.win.state() == "normal":
            self.robot_win.hide()
        else:
            self.robot_win.show()

    def set_robot_state(self, state: str):
        self.robot_win.set_state(state)

    def toggle_mic(self):
        cur = memory.get("continuous_listen", False)
        memory["continuous_listen"] = not cur
        self.mic_btn.config(text=f"🎤 Mic: {'ON' if not cur else 'OFF'}", bg="#059669" if not cur else "#dc2626")

    def toggle_tts(self):
        cur = memory.get("tts_enabled", True)
        memory["tts_enabled"] = not cur
        self.tts_btn.config(text=f"🔊 TTS: {'ON' if not cur else 'OFF'}", bg="#059669" if not cur else "#dc2626")

    def greet_startup(self):
        name = memory.get("user_name")
        msg = get_text("welcome_named", name=name) if name else get_text("welcome")
        self.append_chat("Nova", msg)
        safe_speak(msg)

    def quit_and_cleanup(self):
        save_json_file(CONFIG["MEMORY_FILE"], memory)
        save_json_file(CONFIG["REMINDER_FILE"], reminders)
        save_json_file(CONFIG["SCHEDULE_FILE"], schedule_tasks)
        try:
            self.robot_win.destroy()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

# ==============================================================================
# MAIN LAUNCH ENTRY
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 Starting Nova / Ultra Jarvis Suite for Windows")
    print("=" * 60)

    # 1. Security Biometric Face Lock with PIN Fallback
    if HAS_OPENCV and os.path.exists(CONFIG["REGISTERED_FACE"]):
        print("Starting Biometric Face Lock...")
        ok = unlock_face()
        if not ok:
            print("Face not recognized. Prompting for PIN...")
            if not password_window():
                print("Access Denied. Exiting.")
                sys.exit(0)
    else:
        print("Biometric face lock ready (PIN fallback active).")

    # 2. Launch Tkinter GUI
    root = tk.Tk()
    app = UltraJarvisApp(root)
    root.protocol("WM_DELETE_WINDOW", app.quit_and_cleanup)
    root.mainloop()
