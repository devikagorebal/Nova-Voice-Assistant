"""
command_handler.py - Intent recognition and routing for Nova Voice Assistant
Uses ONLY Python Standard Library
"""

import json
import re
import urllib.parse
import webbrowser
from pathlib import Path
import system_control
import ai_engine

NOTES_FILE = Path(__file__).resolve().parent / "notes.json"

def load_notes():
    if NOTES_FILE.exists():
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_notes(notes):
    try:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2)
        return True
    except Exception:
        return False

def add_note(text):
    notes = load_notes()
    import datetime
    item = {
        "text": text,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }
    notes.append(item)
    save_notes(notes)
    return f"Saved note: '{text}'."

def clear_notes():
    save_notes([])
    return "All notes have been cleared."

def get_notes_summary():
    notes = load_notes()
    if not notes:
        return "You have no saved notes."
    res = f"You have {len(notes)} note(s):\n"
    for i, n in enumerate(notes, 1):
        res += f"{i}. {n['text']} ({n['timestamp']})\n"
    return res.strip()

def process_command(raw_text):
    """
    Parse user command and execute appropriate action.
    Returns:
      response: spoken text
      action: action tag for UI badges
      is_ai: bool indicating if Gemini AI was used
      metadata: extra data (links, details)
    """
    if not raw_text or not raw_text.strip():
        return {
            "response": "I didn't catch that. Please click the mic or type a command.",
            "action": "none",
            "is_ai": False
        }
    
    text = raw_text.strip()
    cmd = text.lower()

    # 1. Google Search Commands (Uses Gemini AI Search)
    google_search_patterns = [
        r"^search\s+(?:google\s+for|on\s+google\s+for|google|for)\s+(.+)",
        r"^google\s+(.+)",
        r"^(?:who\s+is|what\s+is|where\s+is|how\s+to|tell\s+me\s+about)\s+(.+)"
    ]
    
    for pattern in google_search_patterns:
        match = re.search(pattern, cmd)
        if match:
            query = match.group(1).strip()
            # Avoid matching math like "what is 5 + 5"
            if any(op in query for op in ["+", "-", "*", "/", "divided by", "times"]) and any(c.isdigit() for c in query):
                break
            # Open Google search in browser
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(search_url)
            
            # Use AI engine specifically for Google search summary
            ai_summary = ai_engine.perform_google_search_ai(query)
            return {
                "response": ai_summary,
                "action": "google_search",
                "is_ai": True,
                "search_query": query,
                "search_url": search_url
            }

    # 2. Volume Controls
    if any(k in cmd for k in ["volume up", "increase volume", "louder", "turn up volume", "raise volume"]):
        res = system_control.volume_up()
        return {"response": res, "action": "volume_up", "is_ai": False}
        
    if any(k in cmd for k in ["volume down", "decrease volume", "quieter", "turn down volume", "lower volume"]):
        res = system_control.volume_down()
        return {"response": res, "action": "volume_down", "is_ai": False}
        
    if any(k in cmd for k in ["mute volume", "mute sound", "mute", "unmute"]):
        res = system_control.volume_mute()
        return {"response": res, "action": "volume_mute", "is_ai": False}

    # 3. Lock Workstation
    if any(k in cmd for k in ["lock pc", "lock computer", "lock screen", "lock workstation", "lock my pc"]):
        res = system_control.lock_workstation()
        return {"response": res, "action": "lock", "is_ai": False}

    # 4. Battery Status
    if any(k in cmd for k in ["battery", "battery percentage", "battery level", "power remaining"]):
        res = system_control.get_battery_info()
        return {"response": res, "action": "battery", "is_ai": False}

    # 5. Screenshot
    if any(k in cmd for k in ["take screenshot", "take a screenshot", "capture screen", "screenshot"]):
        res = system_control.take_screenshot()
        return {"response": res, "action": "screenshot", "is_ai": False}

    # 6. Date & Time
    if any(k in cmd for k in ["what time is it", "current time", "what's the time", "tell me the time", "today's date", "what is the date", "what day is it"]):
        res = system_control.get_datetime_info()
        return {"response": res, "action": "time", "is_ai": False}

    # 7. Notes
    if cmd.startswith("take a note") or cmd.startswith("note that") or cmd.startswith("remember that") or cmd.startswith("write a note"):
        note_content = re.sub(r"^(take a note|note that|remember that|write a note)\s*(to|that|about)?\s*", "", text, flags=re.IGNORECASE).strip()
        if not note_content:
            note_content = "Untitled Note"
        res = add_note(note_content)
        return {"response": res, "action": "note_add", "is_ai": False}

    if any(k in cmd for k in ["show notes", "show my notes", "read notes", "get notes", "what are my notes"]):
        res = get_notes_summary()
        return {"response": res, "action": "note_view", "is_ai": False}

    if any(k in cmd for k in ["clear notes", "delete notes", "remove notes"]):
        res = clear_notes()
        return {"response": res, "action": "note_clear", "is_ai": False}

    # 8. YouTube Search
    yt_match = re.search(r"(?:search youtube for|play|search on youtube)\s+(.+)", cmd)
    if yt_match and not cmd.startswith("play game"):
        target = yt_match.group(1).replace("on youtube", "").strip()
        res = system_control.search_web(target, engine="youtube")
        return {"response": res, "action": "youtube", "is_ai": False}

    # 9. Wikipedia Search
    wiki_match = re.search(r"(?:search wikipedia for|wiki)\s+(.+)", cmd)
    if wiki_match:
        target = wiki_match.group(1).strip()
        res = system_control.search_web(target, engine="wikipedia")
        return {"response": res, "action": "wikipedia", "is_ai": False}

    # 10. Open specific website
    site_match = re.search(r"open (youtube|google|github|reddit|gmail|chatgpt|twitter|linkedin|amazon|netflix|x\.com|[a-z0-9\-\.]+\.(?:com|org|net|io|edu))", cmd)
    if site_match:
        site = site_match.group(1)
        res = system_control.open_website(site)
        return {"response": res, "action": "website", "is_ai": False}

    # 11. Open Applications
    app_match = re.search(r"open\s+([a-zA-Z0-9\s]+)", cmd)
    if app_match:
        app_target = app_match.group(1).strip()
        if len(app_target) > 1 and app_target not in ["the door", "sesame", "a can"]:
            res = system_control.open_application(app_target)
            return {"response": res, "action": "app_open", "is_ai": False}

    # 12. General Conversational / Math reply (No API needed)
    reply = ai_engine.offline_general_reply(text)
    return {
        "response": reply,
        "action": "general_reply",
        "is_ai": False
    }
