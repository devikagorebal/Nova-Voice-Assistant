"""
system_control.py - Native Windows Controls for Nova Voice Assistant
Uses ONLY Python Standard Library (ctypes, subprocess, os, webbrowser, datetime)
No third-party packages required!
"""

import os
import sys
import ctypes
import subprocess
import webbrowser
import datetime
from pathlib import Path

# Windows Virtual Key Codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

def _send_key(vk_code):
    """Send a single virtual key press and release via ctypes."""
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
        user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        print(f"Error sending key: {e}")
        return False

def volume_up(steps=4):
    """Increase master volume."""
    for _ in range(steps):
        _send_key(VK_VOLUME_UP)
    return "Increased system volume."

def volume_down(steps=4):
    """Decrease master volume."""
    for _ in range(steps):
        _send_key(VK_VOLUME_DOWN)
    return "Decreased system volume."

def volume_mute():
    """Toggle mute system volume."""
    _send_key(VK_VOLUME_MUTE)
    return "Toggled system mute."

def lock_workstation():
    """Lock the Windows computer."""
    try:
        ctypes.windll.user32.LockWorkStation()
        return "Workstation locked successfully."
    except Exception as e:
        return f"Failed to lock workstation: {e}"

def get_battery_info():
    """Get battery percentage and charging status via PowerShell."""
    try:
        cmd = 'Get-CimInstance -ClassName Win32_Battery -ErrorAction SilentlyContinue | Select-Object -Property EstimatedChargeRemaining, BatteryStatus | ConvertTo-Json'
        res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, timeout=5)
        out = res.stdout.strip()
        if not out:
            return "No battery detected (desktop or AC powered)."
        import json
        data = json.loads(out)
        charge = data.get("EstimatedChargeRemaining", "Unknown")
        status_code = data.get("BatteryStatus", 1)
        status_map = {1: "Discharging", 2: "Connected to AC (Charging)", 3: "Fully Charged", 4: "Low", 5: "Critical"}
        status = status_map.get(status_code, "In use")
        return f"Battery is at {charge}% ({status})."
    except Exception as e:
        return "Unable to determine battery status."

def take_screenshot(target_dir=None):
    """Capture screen natively using Windows PowerShell and System.Drawing."""
    if not target_dir:
        # Default to user's Pictures folder or local directory
        target_dir = Path.home() / "Pictures"
        if not target_dir.exists():
            target_dir = Path(__file__).resolve().parent

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = Path(target_dir) / f"Nova_Screenshot_{timestamp}.png"
    
    ps_cmd = f"""
    Add-Type -AssemblyName System.Windows.Forms;
    Add-Type -AssemblyName System.Drawing;
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds;
    $bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height;
    $gfx = [System.Drawing.Graphics]::FromImage($bmp);
    $gfx.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size);
    $bmp.Save('{str(file_path).replace(chr(92), chr(47))}', [System.Drawing.Imaging.ImageFormat]::Png);
    $bmp.Dispose();
    $gfx.Dispose();
    """
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=8)
        if file_path.exists():
            return f"Screenshot saved to {file_path.name} in your Pictures folder."
        else:
            return "Screenshot capture failed."
    except Exception as e:
        return f"Screenshot error: {e}"

def open_application(app_name):
    """Launch popular Windows applications."""
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "files": "explorer.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",
        "paint": "mspaint.exe",
        "mspaint": "mspaint.exe",
        "snipping tool": "snippingtool.exe",
        "snip": "snippingtool.exe",
        "camera": "start microsoft.windows.camera:",
        "settings": "start ms-settings:",
        "control panel": "control.exe",
        "edge": "start msedge:",
        "chrome": "start chrome:",
        "spotify": "start spotify:",
        "whatsapp": "start whatsapp:"
    }
    
    clean_name = app_name.lower().strip()
    target = apps.get(clean_name)
    
    if not target:
        for k, v in apps.items():
            if k in clean_name:
                target = v
                clean_name = k
                break
                
    if not target:
        # Try generic Windows start
        target = f"start {clean_name}"

    try:
        if target.startswith("start "):
            subprocess.Popen(target, shell=True)
        else:
            subprocess.Popen([target], shell=True)
        return f"Opening {clean_name.capitalize()}."
    except Exception as e:
        return f"Could not open {clean_name}: {e}"

def search_web(query, engine="google"):
    """Open a search in default web browser."""
    import urllib.parse
    encoded = urllib.parse.quote_plus(query)
    if engine == "youtube":
        url = f"https://www.youtube.com/results?search_query={encoded}"
        label = "YouTube"
    elif engine == "wikipedia":
        url = f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}"
        label = "Wikipedia"
    else:
        url = f"https://www.google.com/search?q={encoded}"
        label = "Google"

    webbrowser.open(url)
    return f"Searching {label} for '{query}'."

def open_website(site_name):
    """Open standard popular websites."""
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "reddit": "https://www.reddit.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chat.openai.com",
        "twitter": "https://twitter.com",
        "x": "https://x.com",
        "linkedin": "https://www.linkedin.com",
        "amazon": "https://www.amazon.com",
        "netflix": "https://www.netflix.com"
    }
    clean = site_name.lower().strip()
    for name, url in sites.items():
        if name in clean:
            webbrowser.open(url)
            return f"Opening {name.capitalize()}."
    
    if "." in clean:
        url = f"https://{clean}" if not clean.startswith("http") else clean
        webbrowser.open(url)
        return f"Opening {clean}."
    
    return search_web(site_name, "google")

def get_datetime_info():
    """Return formatted current time and date."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d, %Y")
    return f"It is currently {time_str} on {date_str}."
