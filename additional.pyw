import cv2
import requests
import time
from datetime import datetime
import base64
from io import BytesIO
import sys
import json

# Discord webhooks
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]

def capture_image(camera_index=0):
    """Capture image from camera - minimal time to reduce flash."""
    try:
        # Open camera quickly
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # Use DSHOW for Windows
        
        if not cap.isOpened():
            # Try different indices
            for i in range(0, 3):
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    camera_index = i
                    print(f"Found camera at index {i}")
                    break
        
        if not cap.isOpened():
            print("ERROR: Cannot open camera")
            return None
        
        # Minimal settings for speed
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 5)
        
        # Grab a few frames quickly (flash activates here)
        for _ in range(5):
            cap.grab()
        
        # Read the actual frame
        ret, frame = cap.read()
        
        # Release camera IMMEDIATELY (flash should turn off)
        cap.release()
        
        if not ret:
            print("ERROR: Failed to capture frame")
            return None
        
        return frame
        
    except Exception as e:
        print(f"ERROR in capture: {e}")
        return None

def send_to_discord_webhook(image, webhook_url):
    """Send image to Discord webhook with proper formatting."""
    try:
        # Convert image to bytes
        _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        image_bytes = buffer.tobytes()
        
        # Prepare the multipart form data
        files = {
            'file': ('camera_capture.jpg', image_bytes, 'image/jpeg')
        }
        
        # Add timestamp as message content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            'content': f"Camera capture at {timestamp}",
            'username': 'Camera Bot'
        }
        
        # Send to Discord
        response = requests.post(webhook_url, files=files, data=data, timeout=10)
        
        if response.status_code == 204:
            print(f"SUCCESS: Image sent to Discord (204)")
            return True
        elif response.status_code == 429:
            # Rate limited
            retry_after = response.json().get('retry_after', 5)
            print(f"RATE LIMITED: Waiting {retry_after} seconds")
            time.sleep(retry_after)
            return False
        else:
            print(f"ERROR: Discord returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"ERROR sending to Discord: {e}")
        return False

def main():
    """Main function to capture and send images."""
    print("=" * 50)
    print("CAMERA TO DISCORD BOT")
    print("=" * 50)
    
    # Test camera first
    print("\nTesting camera...")
    test_image = capture_image()
    
    if test_image is None:
        print("FAILED: Could not access camera")
        print("Trying alternative camera indices...")
        
        # Try different camera indices
        for i in range(0, 3):
            print(f"Trying camera index {i}...")
            test_image = capture_image(i)
            if test_image is not None:
                print(f"SUCCESS: Camera found at index {i}")
                break
        
        if test_image is None:
            print("ERROR: No camera found. Please check your camera connection.")
            return
    
    print(f"SUCCESS: Camera test passed (Image size: {test_image.shape[1]}x{test_image.shape[0]})")
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Capture and send once")
    print("2. Continuous mode")
    print("3. Test without sending (preview only)")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Single capture
            print("\n" + "=" * 30)
            print("CAPTURING IMAGE...")
            print("=" * 30)
            
            image = capture_image()
            if image is None:
                print("Failed to capture image")
                return
            
            print("Image captured successfully")
            print("Sending to Discord...")
            
            success_count = 0
            for i, webhook in enumerate(DISCORD_WEBHOOKS, 1):
                print(f"\nSending to webhook {i}...")
                if send_to_discord_webhook(image, webhook):
                    success_count += 1
                time.sleep(0.5)  # Small delay between webhooks
            
            print(f"\n{'='*40}")
            print(f"RESULT: Sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks")
            print("="*40)
        
        elif choice == '2':
            # Continuous mode
            try:
                interval = int(input("\nEnter interval in seconds (default: 30): ") or "30")
            except:
                interval = 30
            
            print(f"\nStarting continuous capture every {interval} seconds")
            print("Press CTRL+C to stop\n")
            
            counter = 0
            try:
                while True:
                    counter += 1
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Capture #{counter}")
                    
                    image = capture_image()
                    if image is not None:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        print(f"Image captured ({image.shape[1]}x{image.shape[0]})")
                        
                        # Send to all webhooks
                        for i, webhook in enumerate(DISCORD_WEBHOOKS, 1):
                            print(f"  Sending to webhook {i}...")
                            if send_to_discord_webhook(image, webhook):
                                print(f"    ✓ Sent")
                            else:
                                print(f"    ✗ Failed")
                            time.sleep(1)
                    
                    # Wait for next capture
                    if interval > 0:
                        print(f"\nWaiting {interval} seconds...")
                        for remaining in range(interval, 0, -1):
                            mins, secs = divmod(remaining, 60)
                            print(f"Next capture in: {mins:02d}:{secs:02d}", end='\r')
                            time.sleep(1)
                        print()
                        
            except KeyboardInterrupt:
                print(f"\n\nStopped after {counter} captures")
        
        elif choice == '3':
            # Test mode
            print("\nTest mode - Preview only")
            print("The camera flash/light will activate briefly")
            input("Press Enter to capture (flash will activate)...")
            
            image = capture_image()
            if image is not None:
                print(f"Captured image: {image.shape[1]}x{image.shape[0]}")
                
                # Show preview
                cv2.imshow('Preview - Press any key to close', image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                save = input("Save image to file? (y/n): ").lower()
                if save == 'y':
                    filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, image)
                    print(f"Saved as {filename}")
            else:
                print("Failed to capture image")
        
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\nERROR: {e}")

def send_test_webhook():
    """Test webhook with a simple message."""
    print("\nTesting webhooks with simple message...")
    
    test_message = {
        "content": "Test message from Camera Bot",
        "username": "Camera Tester"
    }
    
    for i, webhook in enumerate(DISCORD_WEBHOOKS, 1):
        print(f"\nTesting webhook {i}...")
        try:
            response = requests.post(webhook, json=test_message, timeout=5)
            if response.status_code == 204:
                print("✓ Webhook working")
            else:
                print(f"✗ Webhook error: {response.status_code}")
        except Exception as e:
            print(f"✗ Webhook failed: {e}")

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import cv2
        import requests
    except ImportError:
        print("ERROR: Required packages not installed")
        print("Please run: pip install opencv-python requests")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("Camera to Discord Bot v2.0")
    print("=" * 40)
    print("IMPORTANT: Camera flash/light cannot be disabled")
    print("           It will turn on briefly during capture")
    print("=" * 40)
    
    # Test webhooks first
    test_webhooks = input("\nTest webhooks before starting? (y/n): ").lower()
    if test_webhooks == 'y':
        send_test_webhook()
    
    # Run main program
    main()
    
    print("\nProgram completed.")
    input("Press Enter to exit...")
