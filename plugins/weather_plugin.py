"""
plugins/weather_plugin.py - Sample Plugin for Nova / Ultra Jarvis Suite
Demonstrates the dynamic plugin extension system (Part 21).
"""

def init_plugin(app):
    """
    Called automatically when the plugin is loaded by the assistant.
    Registers custom commands and adds a greeting.
    """
    app.append_chat("System", "[Plugin: Weather] Initialized successfully.")

def handle_command(app, cmd: str) -> bool:
    """
    Called on user input. Returns True if this plugin handled the command.
    """
    clean = cmd.lower().strip()
    if clean.startswith("forecast ") or clean == "forecast":
        city = clean.replace("forecast", "").strip() or "local area"
        report = f"Weather forecast for {city.title()}: 24°C, Partly Cloudy, 65% Humidity, Wind 12 km/h."
        app.append_chat("Jarvis", report)
        if hasattr(app, "safe_speak"):
            app.safe_speak(f"Here is the forecast for {city}: 24 degrees, partly cloudy.")
        return True
    return False
