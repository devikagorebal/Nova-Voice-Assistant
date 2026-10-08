"""
ai_engine.py - AI Engine for Nova Voice Assistant
Used specifically for Google Search commands and instant knowledge.
Does NOT ask the user for an API key in the UI.
"""

import json
import os
import re
import math
import urllib.request
import urllib.parse
import urllib.error

# Gemini API Key configuration
# Can be set here or via environment variable GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

def search_duckduckgo_instant(query):
    """Zero-config instant web search answer using standard urllib."""
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "NovaAssistant/1.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            abstract = data.get("AbstractText", "").strip()
            heading = data.get("Heading", "").strip()
            
            if abstract:
                # Truncate to 2-3 sentences for voice readability
                sentences = re.split(r'(?<=[.!?]) +', abstract)
                return " ".join(sentences[:3])
            
            # Check related topics
            related = data.get("RelatedTopics", [])
            for item in related:
                if isinstance(item, dict) and "Text" in item:
                    text = item["Text"]
                    if len(text) > 20:
                        sentences = re.split(r'(?<=[.!?]) +', text)
                        return " ".join(sentences[:2])
                        
            if heading:
                return f"Information about {heading} found on the web."
    except Exception:
        pass
    return None

def query_gemini_search(query, api_key=None):
    """Use Gemini API specifically to answer and summarize Google search commands."""
    key = api_key or GEMINI_API_KEY
    if not key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    prompt = f"Provide a direct, concise 2 to 3 sentence factual answer for this Google search query: {query}"
    
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 200
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)
            candidates = res_json.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
    except Exception as e:
        print(f"Gemini API query error: {e}")
        return None
    return None

def perform_google_search_ai(query):
    """
    Execute AI-powered Google search command.
    1. Attempts Gemini API if configured.
    2. Falls back to instant web search engine.
    3. Provides a clean voice-ready summary.
    """
    # 1. Try Gemini API for Google Search
    if GEMINI_API_KEY:
        gemini_result = query_gemini_search(query, GEMINI_API_KEY)
        if gemini_result:
            return gemini_result

    # 2. Try instant web knowledge
    web_result = search_duckduckgo_instant(query)
    if web_result:
        return web_result

    # 3. Clean fallback
    return f"Here is what I found for '{query}'. I have opened Google search in your browser."

def evaluate_math(expression):
    """Safely calculate math expressions without external libraries."""
    clean = expression.replace("x", "*").replace("times", "*").replace("divided by", "/").replace("plus", "+").replace("minus", "-")
    clean = re.sub(r"[^0-9\+\-\*\/\%\(\)\.\s\^]", "", clean).strip()
    clean = clean.replace("^", "**")
    
    if not clean or not re.search(r"\d", clean):
        return None
    
    try:
        result = eval(clean, {"__builtins__": None, "math": math}, {})
        if isinstance(result, float):
            return f"{clean} = {result:.2f}".rstrip('0').rstrip('.')
        return f"{clean} = {result}"
    except Exception:
        return None

def offline_general_reply(prompt):
    """Standard conversational response without requiring any API keys."""
    lower = prompt.lower().strip()
    
    # Math
    if any(k in lower for k in ["calculate", "what is", "solve", "how much is", "plus", "minus", "times", "divided by"]) and any(c.isdigit() for c in lower):
        calc_res = evaluate_math(lower)
        if calc_res:
            return f"The answer is {calc_res}."

    # Identity
    if any(k in lower for k in ["who are you", "what are you", "your name"]):
        return "I am Nova, your personal Windows Voice Assistant."

    if any(k in lower for k in ["who made you", "who created you"]):
        return "I was built using pure Python, HTML, CSS, and JavaScript specifically for Windows."

    if any(k in lower for k in ["how are you", "how are you doing", "how do you do"]):
        return "I am running smoothly and ready to assist you! What would you like me to do?"

    if any(k in lower for k in ["hello", "hi nova", "hey nova", "hey", "greetings"]):
        return "Hello! How can I help you today? You can ask me to open apps, check your battery, adjust volume, or search Google."

    if any(k in lower for k in ["thank you", "thanks"]):
        return "You're very welcome! Let me know if you need anything else."

    if any(k in lower for k in ["joke", "make me laugh"]):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why was the computer cold? Because it left its Windows open!",
            "There are 10 types of people in the world: those who understand binary, and those who don't.",
            "Why did the computer keep freezing? It lost its cache!"
        ]
        import random
        return random.choice(jokes)

    if any(k in lower for k in ["what can you do", "help", "commands"]):
        return "I can control Windows volume, lock your PC, check battery life, take screenshots, open apps (Notepad, Calculator, Settings, etc.), and perform AI Google searches."

    return f"I heard: '{prompt}'. You can ask me to control Windows, open applications, or say 'search Google for...' to search the web."
