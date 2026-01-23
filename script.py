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
    # General game platforms
    "crazygames",
    "poki",
    "kizi",
    "y8",
    "y8 games",
    "armor games",
    "miniclip",
    "addicting games",
    "kongregate",
    "gameflare",
    "friv",
    "friv games",
    "silvergames",
    "lagged",
    "unblocked games",
    "unblocked games 66",
    "unblocked games 76",
    "unblocked games 911",
    "cool math games",
    "math playground games",

    # Popular games
    "roblox",
    "minecraft",
    "fortnite",
    "among us",
    "call of duty",
    "call of duty warzone",
    "league of legends",
    "valorant",
    "counter strike",
    "csgo",
    "dota 2",
    "overwatch",
    "genshin impact",
    "apex legends",
    "pubg",
    "clash royale",
    "clash of clans",
    "brawl stars",
    "fifa",
    "rocket league",

    # Mobile / casual games
    "subway surfers",
    "temple run",
    "geometry dash",
    "bitlife",
    "paper io",
    "slither io",
    "agar io",
    "cookie clicker",
    "idle games",
    "clicker games",

    # French / multilingual gaming phrases
    "jeux gratuits",
    "jeu gratuit",
    "jeux en ligne",
    "joue maintenant",
    "jouer en ligne",
    "spiele kostenlos",
    "online spiele",
    "juegos gratis",
    "jugar ahora",

    # Emulators & retro
    "retro games",
    "classic games",
    "arcade games",
    "flash games",
    "browser games",
    "nes games online",
    "gba games online",

    # Streaming & gaming communities
    "twitch",
    "twitch gaming",
    "kick streaming",
    "youtube gaming",
    "discord gaming",
    "steam",
    "epic games",
    "origin games",
    "battle net"
]

PASSWORD = "stop123"    # Password to toggle tracking
TOGGLE_HOTKEY = "ctrl+alt+p"  # Alternative hotkey to toggle tracking

# Discord Webhook Configuration (BOTH WEBHOOKS)
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]
SEND_SCREENSHOTS = True  # Set to False to disable screenshot sending
SCREENSHOT_DELAY = 0.5   # Delay after detection before taking screenshot (seconds)
HEARTBEAT_INTERVAL = 300  # 5 minutes in seconds

# ---------------- GLOBALS ---------------- #
lock = threading.Lock() # Thread safety
tracking_enabled = True  # Master toggle for tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
detected_targets = set()  # Track already detected targets to avoid duplicate notifications
last_heartbeat_time = time.time()  # Track when last heartbeat was sent
program_start_time = time.time()  # Track program start time

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

def send_to_webhook(webhook_url, payload, screenshot_bytes=None):
    """Send data to a specific webhook URL"""
    try:
        if screenshot_bytes:
            # Create a new BytesIO object for each webhook
            img_byte_arr = io.BytesIO(screenshot_bytes)
            files = {
                'file': ('screenshot.png', img_byte_arr, 'image/png')
            }
            
            # Prepare multipart form data
            if 'embeds' in payload:
                data = {'payload_json': json.dumps(payload)}
                response = requests.post(
                    webhook_url,
                    files=files,
                    data=data,
                    timeout=10
                )
            else:
                # If no embeds, just send with files
                response = requests.post(
                    webhook_url,
                    files=files,
                    data=payload,
                    timeout=10
                )
        else:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
        
        if response.status_code in [200, 204]:
            print(f"[WEBHOOK SUCCESS] Sent to {webhook_url[:40]}...")
            return True
        else:
            print(f"[WEBHOOK ERROR] Failed to send to {webhook_url[:40]}...: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[WEBHOOK ERROR] {e} for {webhook_url[:40]}...")
        return False

def send_to_all_webhooks(payload, screenshot=None):
    """Send message to all configured webhooks"""
    if not DISCORD_WEBHOOKS or all(wh == "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
        print("[DISCORD] No webhooks configured")
        return False
    
    success_count = 0
    threads = []
    
    # Convert screenshot to bytes once
    screenshot_bytes = None
    if screenshot and SEND_SCREENSHOTS:
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        screenshot_bytes = img_byte_arr.getvalue()  # Get raw bytes
        
        # Add screenshot info to payload
        if 'embeds' in payload:
            if 'content' not in payload or not payload['content']:
                payload['content'] = "📸 **Screenshot captured below:**"
    
    for webhook_url in DISCORD_WEBHOOKS:
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            continue
            
        # Create thread for each webhook
        if screenshot_bytes:
            thread = threading.Thread(
                target=send_to_webhook,
                args=(webhook_url, payload),
                kwargs={'screenshot_bytes': screenshot_bytes}
            )
        else:
            thread = threading.Thread(
                target=send_to_webhook,
                args=(webhook_url, payload)
            )
        
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join(timeout=15)  # 15 second timeout per webhook
        
        # Check if thread completed successfully
        if not thread.is_alive():
            success_count += 1
    
    print(f"[DISCORD] Sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks")
    return success_count > 0

def send_discord_alert(title, keyword, screenshot=None):
    """Send alert to Discord webhooks with optional screenshot"""
    # Prepare the message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = {
        "title": "⚠️ Target Application Detected",
        "description": f"**Window Title:** `{title}`\n**Matched Keyword:** `{keyword}`\n**Time:** `{current_time}`",
        "color": 16711680,  # Red color
        "footer": {
            "text": "Tracker System"
        }
    }
    
    payload = {
        "embeds": [embed],
        "content": f"🚨 **Target detected:** {title}"
    }
    
    return send_to_all_webhooks(payload, screenshot)

def send_discord_status(status):
    """Send tracking status to Discord"""
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
        
        return send_to_all_webhooks(payload)
        
    except Exception as e:
        print(f"[DISCORD STATUS ERROR] {e}")
        return False

def send_heartbeat():
    """Send heartbeat webhook to confirm PC is active"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime_seconds = int(time.time() - program_start_time)
        
        # Convert uptime to readable format
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        embed = {
            "title": "💓 PC Heartbeat",
            "description": f"**PC is active and running**\n**Time:** `{current_time}`\n**Uptime:** `{hours}h {minutes}m {seconds}s`\n**Tracking Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`",
            "color": 3447003,  # Blue color
            "footer": {
                "text": "Tracker System"
            }
        }
        
        payload = {
            "embeds": [embed]
        }
        
        success = send_to_all_webhooks(payload)
        if success:
            print(f"[HEARTBEAT] Sent to all webhooks at {current_time}")
        return success
            
    except Exception as e:
        print(f"[HEARTBEAT ERROR] {e}")
        return False

def send_startup_message():
    """Send webhook when the program starts"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        embed = {
            "title": "🚀 Tracker Started",
            "description": f"**Tracker system has been launched**\n**Start Time:** `{current_time}`\n**Initial Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`",
            "color": 3066993,  # Green color
            "footer": {
                "text": "Tracker System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": "📱 **System Online** - Tracker is now active"
        }
        
        success = send_to_all_webhooks(payload)
        if success:
            print(f"[STARTUP] Message sent to all webhooks at {current_time}")
        return success
            
    except Exception as e:
        print(f"[STARTUP ERROR] {e}")
        return False

def toggle_tracking():
    """Toggle tracking on/off"""
    global tracking_enabled, password_buffer
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    print(f"[TRACKING] Tracking {status}")
    
    # Send Discord notification about status change
    threading.Thread(target=send_discord_status, args=(status,), daemon=True).start()
    
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

# ---------------- HEARTBEAT THREAD ---------------- #
def heartbeat_monitor():
    """Periodically send heartbeat every 5 minutes"""
    global last_heartbeat_time
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to send heartbeat
            if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                threading.Thread(target=send_heartbeat, daemon=True).start()
                last_heartbeat_time = current_time
            
            # Sleep for 1 minute and check again
            time.sleep(60)
            
        except Exception as e:
            print(f"[HEARTBEAT MONITOR ERROR] {e}")
            time.sleep(60)

# ---------------- MAIN LOOP ---------------- #
print("[SYSTEM] Monitoring started...")
print("[SYSTEM] Tracking is ENABLED by default")

# Send startup webhook immediately
if DISCORD_WEBHOOKS and any(wh != "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
    print(f"[STARTUP] Sending startup webhook to {len(DISCORD_WEBHOOKS)} webhooks...")
    threading.Thread(target=send_startup_message, daemon=True).start()
    
    # Start heartbeat monitor in a separate thread
    heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
    heartbeat_thread.start()
    print(f"[HEARTBEAT] Heartbeat monitor started (every {HEARTBEAT_INTERVAL//60} minutes)")
else:
    print("[DISCORD] No webhooks configured - skipping startup and heartbeat messages")

# Test Discord connections
valid_webhooks = []
for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
    if webhook_url and webhook_url != "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print(f"[DISCORD] Webhook {i} configured")
        try:
            # Just check if URL looks valid, don't actually send GET request
            if webhook_url.startswith("https://discord.com/api/webhooks/") or webhook_url.startswith("https://discordapp.com/api/webhooks/"):
                print(f"[DISCORD] Webhook {i} URL format is valid")
                valid_webhooks.append(webhook_url)
            else:
                print(f"[DISCORD WARNING] Webhook {i} has unusual format")
                valid_webhooks.append(webhook_url)
        except:
            print(f"[DISCORD] Could not test webhook {i} (will still try to post)")
            valid_webhooks.append(webhook_url)

if valid_webhooks:
    print(f"[DISCORD] {len(valid_webhooks)}/{len(DISCORD_WEBHOOKS)} webhooks are valid - Screenshots: {SEND_SCREENSHOTS}")
else:
    print("[DISCORD] No valid webhooks configured - skipping Discord alerts")

# Setup keyboard listener
kb_listener = setup_keyboard_listener()

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

                if detected:
                    keyword = get_matching_keyword(title)
                    
                    # Use a unique identifier for this detection
                    detection_id = f"{title}_{keyword}_{int(time.time())}"
                    
                    if detection_id not in detected_targets:
                        detected_targets.add(detection_id)
                        
                        print(f"[DETECTION] Target detected: '{title}' (Keyword: {keyword})")
                        
                        # Small delay before taking screenshot to ensure window is focused
                        time.sleep(SCREENSHOT_DELAY)
                        
                        # Take screenshot in main thread
                        screenshot = take_screenshot() if SEND_SCREENSHOTS else None
                        
                        # Send alert to both webhooks
                        alert_thread = threading.Thread(
                            target=send_discord_alert,
                            args=(title, keyword, screenshot),
                            daemon=True
                        )
                        alert_thread.start()
                        
                        # Clean up detected targets after 5 minutes
                        threading.Timer(300, lambda: detected_targets.discard(detection_id)).start()

            except Exception as e:
                print(f"[ERROR] {e}")
        
        # Sleep regardless of tracking state
        time.sleep(0.1)

except KeyboardInterrupt:
    print("[EXIT] Interrupted by user.")

finally:
    # Cleanup
    keyboard.unhook_all()
    print("[SYSTEM] Keyboard listeners stopped")
