import time
import time
import threading
import keyboard
import requests
import io
from datetime import datetime
import json
import cv2
import numpy as np

# ---------------- CONFIG ---------------- #
PASSWORD = "stop123"    # Password to toggle tracking
TOGGLE_HOTKEY = "ctrl+alt+p"  # Alternative hotkey to toggle tracking

# Discord Webhook Configuration (BOTH WEBHOOKS)
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]
SEND_PHOTOS = True  # Set to False to disable photo sending
PHOTO_INTERVAL = 300  # 5 minutes in seconds

# Camera Configuration
CAMERA_INDEX = 0  # Usually 0 for default camera, 1 for external camera
CAMERA_RESOLUTION = (1280, 720)  # Width, Height
PHOTO_QUALITY = 95  # JPEG quality (0-100)

# ---------------- GLOBALS ---------------- #
tracking_enabled = True  # Master toggle for photo tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
program_start_time = time.time()  # Track program start time
last_photo_time = 0  # Track when last photo was taken
camera = None  # Camera object

def initialize_camera():
    """Initialize the camera"""
    global camera
    try:
        # Release camera if already open
        if camera is not None:
            camera.release()
            time.sleep(1)
        
        # Initialize camera
        camera = cv2.VideoCapture(CAMERA_INDEX)
        
        # Set camera resolution
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
        
        # Allow camera to warm up
        time.sleep(2)
        
        # Test capture
        success, frame = camera.read()
        if success:
            print(f"[CAMERA] Successfully initialized (Resolution: {CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]})")
            return True
        else:
            print("[CAMERA] Failed to capture test frame")
            return False
            
    except Exception as e:
        print(f"[CAMERA ERROR] Initialization failed: {e}")
        return False

def take_photo():
    """Take a photo using the webcam"""
    global camera
    
    try:
        if camera is None:
            print("[CAMERA] Camera not initialized, attempting to initialize...")
            if not initialize_camera():
                return None
        
        # Capture frame
        success, frame = camera.read()
        
        if not success:
            print("[CAMERA] Failed to capture frame, reinitializing...")
            # Try to reinitialize camera
            if initialize_camera():
                success, frame = camera.read()
                if not success:
                    print("[CAMERA] Still failed after reinitialization")
                    return None
        
        if frame is not None:
            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Add timestamp to photo
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame_rgb, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            print(f"[PHOTO] Photo captured at {timestamp}")
            return frame_rgb
        else:
            print("[CAMERA] Captured frame is None")
            return None
            
    except Exception as e:
        print(f"[CAMERA ERROR] {e}")
        return None

def convert_photo_to_bytes(photo):
    """Convert photo to bytes for sending"""
    try:
        if photo is None:
            return None
        
        # Convert RGB back to BGR for saving with OpenCV
        photo_bgr = cv2.cvtColor(photo, cv2.COLOR_RGB2BGR)
        
        # Encode as JPEG
        success, encoded_photo = cv2.imencode('.jpg', photo_bgr, 
                                              [cv2.IMWRITE_JPEG_QUALITY, PHOTO_QUALITY])
        
        if success:
            return encoded_photo.tobytes()
        else:
            print("[PHOTO] Failed to encode photo")
            return None
            
    except Exception as e:
        print(f"[PHOTO ERROR] {e}")
        return None

def send_to_webhook(webhook_url, payload, photo_bytes=None):
    """Send data to a specific webhook URL"""
    try:
        if photo_bytes:
            # Create a new BytesIO object for each webhook
            photo_io = io.BytesIO(photo_bytes)
            files = {
                'file': ('photo.jpg', photo_io, 'image/jpeg')
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

def send_to_all_webhooks(payload, photo=None):
    """Send message to all configured webhooks"""
    if not DISCORD_WEBHOOKS or all(wh == "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
        print("[DISCORD] No webhooks configured")
        return False
    
    success_count = 0
    threads = []
    
    # Convert photo to bytes once
    photo_bytes = None
    if photo and SEND_PHOTOS:
        photo_bytes = convert_photo_to_bytes(photo)
        if photo_bytes:
            # Add photo info to payload
            if 'embeds' in payload:
                if 'content' not in payload or not payload['content']:
                    payload['content'] = "📸 **Photo captured below:**"
        else:
            print("[PHOTO] Failed to convert photo to bytes, sending without photo")
    
    for webhook_url in DISCORD_WEBHOOKS:
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            continue
            
        # Create thread for each webhook
        if photo_bytes:
            thread = threading.Thread(
                target=send_to_webhook,
                args=(webhook_url, payload),
                kwargs={'photo_bytes': photo_bytes}
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

def send_discord_photo(photo=None, message="Periodic Photo"):
    """Send photo to Discord webhooks"""
    # Prepare the message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed = {
        "title": f"📷 {message}",
        "description": f"**Time:** `{current_time}`\n**Photo Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`\n**Resolution:** `{CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]}`",
        "color": 3447003,  # Blue color
        "footer": {
            "text": "Photo System"
        }
    }
    
    payload = {
        "embeds": [embed],
        "content": f"🖼️ **{message}**"
    }
    
    return send_to_all_webhooks(payload, photo)

def send_discord_status(status):
    """Send tracking status to Discord"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = 65280 if status == "ENABLED" else 16711680  # Green for enabled, red for disabled
        
        embed = {
            "title": f"🔄 Photo Tracking {status}",
            "description": f"Photo tracking has been **{status.lower()}**\n**Time:** `{current_time}`",
            "color": color,
            "footer": {
                "text": "Photo System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": f"📊 **Photo System Status Changed**"
        }
        
        return send_to_all_webhooks(payload)
        
    except Exception as e:
        print(f"[DISCORD STATUS ERROR] {e}")
        return False

def send_startup_message():
    """Send webhook when the program starts with initial photo"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Take initial photo
        print("[STARTUP] Taking initial photo...")
        photo = take_photo()
        
        embed = {
            "title": "🚀 Photo System Started",
            "description": f"**System has been launched**\n**Start Time:** `{current_time}`\n**Initial Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`\n**Photo Interval:** `{PHOTO_INTERVAL//60} minutes`\n**Camera Resolution:** `{CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]}`",
            "color": 3066993,  # Green color
            "footer": {
                "text": "Photo System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": "📱 **System Online** - Photo system is now active"
        }
        
        success = send_to_all_webhooks(payload, photo)
        if success:
            print(f"[STARTUP] Message and initial photo sent to all webhooks at {current_time}")
        return success
            
    except Exception as e:
        print(f"[STARTUP ERROR] {e}")
        return False

def toggle_tracking():
    """Toggle photo tracking on/off"""
    global tracking_enabled, password_buffer
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    print(f"[PHOTO SYSTEM] Photo tracking {status}")
    
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
    print(f"[HOTKEY] Press '{TOGGLE_HOTKEY}' to toggle photo tracking")
    print(f"[PASSWORD] Type '{PASSWORD}' to toggle photo tracking")
    
    # General key listener for password typing
    keyboard.hook(on_key_event, suppress=False)
    
    return keyboard

def take_periodic_photo():
    """Take and send photo if tracking is enabled"""
    global last_photo_time
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to take a photo (and tracking is enabled)
            if (current_time - last_photo_time >= PHOTO_INTERVAL) and tracking_enabled:
                print(f"[PHOTO] Taking periodic photo...")
                photo = take_photo()
                
                if photo is not None:
                    # Send to Discord
                    threading.Thread(
                        target=send_discord_photo, 
                        args=(photo, "Periodic Photo"),
                        daemon=True
                    ).start()
                else:
                    print("[PHOTO] Failed to capture photo, skipping this interval")
                
                last_photo_time = current_time
                print(f"[PHOTO] Next photo in {PHOTO_INTERVAL//60} minutes")
            
            # Sleep for 30 seconds and check again
            time.sleep(30)
            
        except Exception as e:
            print(f"[PHOTO MONITOR ERROR] {e}")
            time.sleep(30)

def cleanup():
    """Cleanup resources before exit"""
    global camera
    print("[CLEANUP] Releasing camera...")
    if camera is not None:
        camera.release()
    cv2.destroyAllWindows()
    print("[CLEANUP] Camera released")

# ---------------- MAIN PROGRAM ---------------- #
print("[SYSTEM] Photo system started...")
print("[SYSTEM] Photo tracking is ENABLED by default")
print(f"[SYSTEM] Photos will be taken every {PHOTO_INTERVAL//60} minutes")

# Initialize last photo time
last_photo_time = time.time()

# Initialize camera
print("[CAMERA] Initializing camera...")
if not initialize_camera():
    print("[CAMERA] WARNING: Could not initialize camera. The system will still run but photos will fail.")

# Send startup webhook with initial photo
if DISCORD_WEBHOOKS and any(wh != "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
    print(f"[STARTUP] Sending startup message to {len(DISCORD_WEBHOOKS)} webhooks...")
    threading.Thread(target=send_startup_message, daemon=True).start()
    
    # Start photo monitor in a separate thread
    photo_thread = threading.Thread(target=take_periodic_photo, daemon=True)
    photo_thread.start()
    print(f"[PHOTO] Photo monitor started (every {PHOTO_INTERVAL//60} minutes)")
else:
    print("[DISCORD] No webhooks configured - skipping startup and periodic photos")

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
    print(f"[DISCORD] {len(valid_webhooks)}/{len(DISCORD_WEBHOOKS)} webhooks are valid - Photos: {SEND_PHOTOS}")
else:
    print("[DISCORD] No valid webhooks configured - skipping Discord alerts")

# Setup keyboard listener
kb_listener = setup_keyboard_listener()

try:
    print("[SYSTEM] Photo system is running. Press Ctrl+C to exit.")
    print("[SYSTEM] The system will take:")
    print("  - 1 photo immediately on startup")
    print(f"  - 1 photo every {PHOTO_INTERVAL//60} minutes while tracking is enabled")
    print(f"[CAMERA] Using camera index {CAMERA_INDEX} at {CAMERA_RESOLUTION[0]}x{CAMERA_RESOLUTION[1]} resolution")
    
    # Keep the main thread alive
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("[EXIT] Interrupted by user.")

finally:
    # Cleanup
    cleanup()
    keyboard.unhook_all()
    print("[SYSTEM] Keyboard listeners stopped")
    print("[SYSTEM] Photo system terminated")
