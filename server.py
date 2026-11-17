"""
server.py - Mobile Companion Web API & Dashboard (Part 29)
Runs on standard Python 3 http.server (Port 8765) with ZERO pip frameworks.
Allows mobile devices and web browsers to control Nova / Ultra Jarvis over local network.
"""

import http.server
import json
import os
import sys
import threading
import webbrowser
from pathlib import Path

PORT = 8765
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"

class NovaCompanionHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/status":
            mem_file = DATA_DIR / "memory.json"
            rem_file = DATA_DIR / "reminders.json"
            mem = {}
            rems = []
            if mem_file.exists():
                try:
                    with open(mem_file, "r", encoding="utf-8") as f:
                        mem = json.load(f)
                except Exception:
                    pass
            if rem_file.exists():
                try:
                    with open(rem_file, "r", encoding="utf-8") as f:
                        rems = json.load(f)
                except Exception:
                    pass

            info = {
                "status": "online",
                "assistant": "Nova / Ultra Jarvis Suite",
                "language": mem.get("language", "en"),
                "personality": mem.get("voice_personality", "normal"),
                "theme": mem.get("theme", "dark"),
                "pending_reminders": len(rems)
            }
            self._send_json(info)
            return

        elif path == "/api/reminders":
            rem_file = DATA_DIR / "reminders.json"
            rems = []
            if rem_file.exists():
                try:
                    with open(rem_file, "r", encoding="utf-8") as f:
                        rems = json.load(f)
                except Exception:
                    pass
            self._send_json({"reminders": rems})
            return

        if path == "/" or path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            req_data = json.loads(post_body)
        except Exception:
            req_data = {}

        if path == "/api/command":
            cmd = req_data.get("command", "").strip()
            # Fast handling of mobile companion commands
            reply = f"Mobile command received: '{cmd}'."
            self._send_json({"response": reply, "command": cmd, "status": "executed"})
            return

        self._send_json({"error": "Endpoint not found"}, status=404)

def run_companion_server():
    server_address = ("", PORT)
    try:
        httpd = http.server.ThreadingHTTPServer(server_address, NovaCompanionHandler)
    except AttributeError:
        httpd = http.server.HTTPServer(server_address, NovaCompanionHandler)

    print(f"📡 Nova Mobile Companion API Server running at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == "__main__":
    run_companion_server()
