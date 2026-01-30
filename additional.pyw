import cv2
import requests
from io import BytesIO
import time
from datetime import datetime

# Discord webhooks
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]

def capture_image():
    """Capture a single image from the default camera."""
    # Open the default camera (usually 0)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    
    # Give camera time to adjust to light
    time.sleep(0.5)
    
    # Capture a frame
    ret, frame = cap.read()
    
    # Release the camera
    cap.release()
    
    if not ret:
        print("Error: Could not capture image.")
        return None
    
    return frame

def send_to_discord(image, webhook_url, message=None):
    """Send image to a Discord webhook."""
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
            print(f"Image sent successfully to Discord!")
            return True
        else:
            print(f"Error sending to Discord: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False

def capture_and_send():
    """Capture image and send to all webhooks."""
    print("Capturing image...")
    image = capture_image()
    
    if image is None:
        print("Failed to capture image.")
        return
    
    # Create timestamp for optional message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Camera capture at {timestamp}"
    
    # Send to all webhooks
    success_count = 0
    for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
        print(f"Sending to webhook {i}...")
        if send_to_discord(image, webhook_url, message):
            success_count += 1
    
    print(f"Successfully sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks.")

def continuous_capture(interval_seconds=10):
    """Continuously capture and send images at specified intervals."""
    print("Starting continuous capture...")
    print(f"Press Ctrl+C to stop.")
    print(f"Interval: {interval_seconds} seconds")
    
    try:
        while True:
            capture_and_send()
            print(f"Waiting {interval_seconds} seconds...")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Install required packages if needed
    # pip install opencv-python requests
    
    print("Discord Camera Capture Script")
    print("=" * 30)
    
    # Test camera
    print("Testing camera...")
    test_capture = cv2.VideoCapture(0)
    if not test_capture.isOpened():
        print("Error: No camera found or camera is in use.")
        exit(1)
    test_capture.release()
    print("Camera test passed!")
    
    # Choose mode
    print("\nSelect mode:")
    print("1. Capture and send once")
    print("2. Continuous capture")
    print("3. Single capture and view before sending")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        # Single capture and send
        capture_and_send()
        
    elif choice == '2':
        # Continuous capture
        try:
            interval = int(input("Enter interval in seconds (default: 10): ") or "10")
        except ValueError:
            interval = 10
        continuous_capture(interval)
        
    elif choice == '3':
        # Preview and send
        print("Capturing image...")
        image = capture_image()
        
        if image is not None:
            # Show preview
            cv2.imshow('Preview (Press any key to send, ESC to cancel)', image)
            key = cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            if key != 27:  # Not ESC
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = f"Camera capture at {timestamp}"
                
                success_count = 0
                for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
                    print(f"Sending to webhook {i}...")
                    if send_to_discord(image, webhook_url, message):
                        success_count += 1
                
                print(f"Successfully sent to {success_count}/{len(DISCORD_WEBHOOKS)} webhooks.")
            else:
                print("Cancelled.")
        else:
            print("Failed to capture image.")
            
    else:
        print("Invalid choice. Exiting.")
