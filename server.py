"""
server.py - Pure Python HTTP Server for Nova Voice Assistant
NO Flask, NO Django, NO external frameworks.
Runs with standard Python 3: python server.py
"""

import http.server
import json
import os
import sys
import webbrowser
from pathlib import Path
import command_handler
import ai_engine
import system_control

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent

class NovaRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler supporting API endpoints and static files."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def _send_json_response(self, data, status_code=200):
        """Send formatted JSON response."""
        response_bytes = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for static assets and API status."""
        path = self.path.split("?")[0]
        
        if path == "/api/status":
            info = {
                "status": "online",
                "name": "Nova",
                "battery": system_control.get_battery_info(),
                "time": system_control.get_datetime_info()
            }
            self._send_json_response(info)
            return

        elif path == "/api/notes":
            notes = command_handler.load_notes()
            self._send_json_response({"notes": notes})
            return

        elif path == "/api/config":
            config = ai_engine.load_config()
            # Mask API key for security
            masked_key = ""
            if config.get("gemini_api_key"):
                raw = config["gemini_api_key"]
                masked_key = raw[:4] + "..." + raw[-4:] if len(raw) > 8 else "***"
            self._send_json_response({
                "has_api_key": bool(config.get("gemini_api_key")),
                "masked_api_key": masked_key,
                "assistant_name": config.get("assistant_name", "Nova")
            })
            return

        # Serve index.html or standard files
        if path == "/" or path == "":
            self.path = "/index.html"
            
        return super().do_GET()

    def do_POST(self):
        """Handle incoming command and config updates."""
        path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            req_data = json.loads(post_body)
        except Exception:
            req_data = {}

        if path == "/api/command":
            user_text = req_data.get("command", "")
            result = command_handler.process_command(user_text)
            self._send_json_response(result)
            return

        elif path == "/api/config":
            new_key = req_data.get("gemini_api_key")
            new_name = req_data.get("assistant_name")
            update_data = {}
            if new_key is not None:
                update_data["gemini_api_key"] = new_key.strip()
            if new_name is not None:
                update_data["assistant_name"] = new_name.strip()
            
            ai_engine.save_config(update_data)
            self._send_json_response({"success": True, "message": "Settings updated successfully."})
            return

        elif path == "/api/notes/clear":
            command_handler.clear_notes()
            self._send_json_response({"success": True, "message": "Notes cleared."})
            return

        self._send_json_response({"error": "Endpoint not found"}, status_code=404)

def run_server():
    server_address = ("", PORT)
    try:
        httpd = http.server.ThreadingHTTPServer(server_address, NovaRequestHandler)
    except AttributeError:
        # Fallback for Python versions without ThreadingHTTPServer
        httpd = http.server.HTTPServer(server_address, NovaRequestHandler)
        
    url = f"http://localhost:{PORT}"
    print("=" * 60)
    print("  ✨ NOVA - Intelligent Windows Voice Assistant ✨")
    print("=" * 60)
    print(f"Server is running at: {url}")
    print("Opening Nova in your default browser...")
    print("Press Ctrl+C to stop the assistant.")
    print("=" * 60)
    
    # Open browser automatically
    webbrowser.open(url)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Nova Assistant server. Goodbye!")
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    run_server()
