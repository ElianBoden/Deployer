# github_launcher.pyw - Memory-optimized using GitHub API for version checking
import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import traceback
import threading
import json
import psutil
from datetime import datetime
import urllib.parse
import urllib.error
import ssl
import queue
import atexit
import base64
import hashlib
ssl._create_default_https_context = ssl._create_unverified_context

# ============================================================================
# CONFIGURATION TABLE - Edit these values directly in the script
# ============================================================================

CONFIG = {
    # Update checking
    "update_check_interval": 15,  # Check every 5 seconds (testing)
    
    # GitHub repository
    "repository_owner": "ElianBoden",
    "repository_name": "Deployer",
    "branch": "main",
    
    # File paths in repository
    "script_path": "script.py",
    "additional_script_path": "additional.pyw",
    "requirements_path": "requirements.txt",
    
    # GitHub token (leave empty for public repos, add token for private/higher limits)
    "github_token": "",
    
    # Discord notifications
    "enable_discord_logging": True,
    
    # Discord webhooks for error notifications
    "discord_webhooks": [
        "https://discordapp.com/api/webhooks/1464318683852832823/vF_b6uHJw7Mmo8TAvQTImzYX2Z4wzIADgPK9W3QsVBSE639CanUCr8iaer1y9_9yJqJ0",
        "https://discord.com/api/webhooks/1464319002531860563/tWigsqZ_oXEXXPa_nB0VsipH1O_SLUGel5rw-YH2iy4qg65__Gl-CVNzs5UJbaXVqzvr"
    ],
    
    # Performance settings
    "cpu_monitor_interval": 60,  # Check CPU usage every 60 seconds
    "max_cpu_percent": 5.0,      # Warning threshold for CPU usage
    "min_update_interval": 15,   # Minimum time between update checks (seconds) - NOTE: This overrides update_check_interval if smaller
    "command_poll_interval": 5,  # Check for commands every 5 seconds
    
    # Byte verification settings
    "enable_byte_verification": False,  # Enable byte size verification
    "byte_verification_retries": 10,    # Number of times to retry if byte size doesn't change
    "byte_verification_delay": 10,     # Delay between byte verification retries (seconds)
    
    # Cache control
    "enable_cache_control": True,       # Add cache-control headers to bypass CDN
    "cache_busting": True,              # Add cache-busting query parameters
}

# ============================================================================
# END OF CONFIGURATION - DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

# Global tracking
current_script_process = None
current_additional_script_process = None
rate_limit_wait = 0
initial_setup_complete = False
script_output_buffer = []
additional_script_output_buffer = []
MAX_OUTPUT_BUFFER = 100
webhook_queue = queue.Queue()
shutdown_event = threading.Event()
process = None  # For CPU monitoring
last_update_check = 0
update_check_count = 0

# Byte verification tracking
file_size_cache = {}  # Cache for file sizes: {filename: {sha: size, last_check: timestamp}}

def get_cpu_usage():
    """Get current CPU and memory usage"""
    try:
        if process:
            cpu_percent = process.cpu_percent(interval=0.5)  # Use longer interval for more accuracy
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "threads": process.num_threads()
            }
    except:
        pass
    return {"cpu_percent": 0, "memory_mb": 0, "threads": 0}

def log_cpu_usage():
    """Log CPU usage periodically"""
    cpu_info = get_cpu_usage()
    print(f"[CPU] Usage: {cpu_info['cpu_percent']}% | Memory: {cpu_info['memory_mb']}MB | Threads: {cpu_info['threads']}")
    return cpu_info

# Helper function to get config (for backward compatibility)
def load_config():
    """Load configuration from the CONFIG table"""
    return CONFIG.copy()

def show_config():
    """Display current configuration"""
    print("\n" + "=" * 70)
    print("CURRENT CONFIGURATION")
    print("=" * 70)
    
    for key, value in CONFIG.items():
        if key == "github_token" and value:
            masked_token = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
            print(f"  {key:25}: {masked_token}")
        elif key == "discord_webhooks":
            print(f"  {key:25}: {len(value)} webhook(s) configured")
        else:
            print(f"  {key:25}: {value}")
    
    print("=" * 70)
    print("To edit configuration, modify the CONFIG dictionary at the top of the script.")
    print("=" * 70)

def edit_config_interactive():
    """Interactive config editor"""
    print("\n" + "=" * 70)
    print("INTERACTIVE CONFIG EDITOR")
    print("=" * 70)
    
    config_keys = list(CONFIG.keys())
    
    while True:
        print("\nCurrent configuration:")
        for i, key in enumerate(config_keys, 1):
            value = CONFIG[key]
            if key == "github_token" and value:
                masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "****"
                print(f"  {i:2}. {key:25}: {masked}")
            elif key == "discord_webhooks":
                print(f"  {i:2}. {key:25}: {len(value)} webhook(s)")
            else:
                print(f"  {i:2}. {key:25}: {value}")
        
        print(f"\n  {len(config_keys) + 1:2}. Show all config (including tokens)")
        print(f"  {len(config_keys) + 2:2}. Exit editor")
        
        try:
            choice = input("\nSelect option to edit (number): ").strip()
            if not choice:
                continue
                
            if choice == str(len(config_keys) + 1):
                # Show all including unmasked tokens
                print("\n" + "=" * 70)
                print("FULL CONFIGURATION (INCLUDING TOKENS)")
                print("=" * 70)
                for key, value in CONFIG.items():
                    print(f"  {key:25}: {value}")
                print("=" * 70)
                continue
            elif choice == str(len(config_keys) + 2):
                print("\nExiting editor...")
                break
            
            choice_num = int(choice) - 1
            if 0 <= choice_num < len(config_keys):
                key = config_keys[choice_num]
                current_value = CONFIG[key]
                
                print(f"\nEditing: {key}")
                print(f"Current value: {current_value}")
                
                if key == "enable_discord_logging":
                    new_value = input("Enable Discord logging? (yes/no) [yes]: ").strip().lower()
                    if new_value == "":
                        new_value = "yes"
                    CONFIG[key] = new_value in ["yes", "y", "true", "1"]
                    print(f"✓ Updated {key} to: {CONFIG[key]}")
                
                elif key == "discord_webhooks":
                    print("\nCurrent webhooks:")
                    for i, webhook in enumerate(current_value, 1):
                        print(f"  {i}. {webhook[:60]}...")
                    
                    print("\nOptions:")
                    print("  1. Add new webhook")
                    print("  2. Remove webhook")
                    print("  3. Clear all webhooks")
                    print("  4. Cancel")
                    
                    sub_choice = input("\nSelect option: ").strip()
                    if sub_choice == "1":
                        new_webhook = input("Enter new Discord webhook URL: ").strip()
                        if new_webhook:
                            CONFIG[key].append(new_webhook)
                            print(f"✓ Webhook added. Total: {len(CONFIG[key])}")
                    elif sub_choice == "2" and current_value:
                        remove_idx = input(f"Enter webhook number to remove (1-{len(current_value)}): ").strip()
                        try:
                            remove_idx = int(remove_idx) - 1
                            if 0 <= remove_idx < len(current_value):
                                removed = CONFIG[key].pop(remove_idx)
                                print(f"✓ Removed webhook: {removed[:60]}...")
                        except:
                            print("✗ Invalid number")
                    elif sub_choice == "3":
                        CONFIG[key] = []
                        print("✓ All webhooks cleared")
                
                elif isinstance(current_value, int):
                    new_value = input(f"Enter new value for {key} [{current_value}]: ").strip()
                    if new_value == "":
                        print("✓ Value unchanged")
                    else:
                        try:
                            CONFIG[key] = int(new_value)
                            print(f"✓ Updated {key} to: {CONFIG[key]}")
                        except:
                            print("✗ Invalid number")
                
                elif isinstance(current_value, bool):
                    new_value = input(f"Enable {key}? (yes/no) [{current_value}]: ").strip().lower()
                    if new_value == "":
                        print("✓ Value unchanged")
                    else:
                        CONFIG[key] = new_value in ["yes", "y", "true", "1"]
                        print(f"✓ Updated {key} to: {CONFIG[key]}")
                
                else:
                    new_value = input(f"Enter new value for {key} [{current_value}]: ").strip()
                    if new_value == "":
                        print("✓ Value unchanged")
                    else:
                        CONFIG[key] = new_value
                        print(f"✓ Updated {key} to: {CONFIG[key]}")
            else:
                print("✗ Invalid option")
                
        except ValueError:
            print("✗ Please enter a number")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("CONFIGURATION SAVED")
    print("=" * 70)
    show_config()

def get_tracker_folder():
    """Get path to tracker folder in AppData - uses Roaming"""
    appdata_roaming = os.getenv('APPDATA')
    tracker_folder = os.path.join(appdata_roaming, "GitHubLauncher")
    os.makedirs(tracker_folder, exist_ok=True)
    return tracker_folder

def get_version_tracker_path(filename):
    """Get path to version tracker file"""
    tracker_folder = get_tracker_folder()
    return os.path.join(tracker_folder, f".{filename}_version.txt")

def get_byte_tracker_path(filename):
    """Get path to byte size tracker file"""
    tracker_folder = get_tracker_folder()
    return os.path.join(tracker_folder, f".{filename}_bytes.txt")

def get_hash_tracker_path(filename):
    """Get path to content hash tracker file"""
    tracker_folder = get_tracker_folder()
    return os.path.join(tracker_folder, f".{filename}_hash.txt")

def get_current_version(filename):
    """Get current stored version (content SHA)"""
    tracker_file = get_version_tracker_path(filename)
    if os.path.exists(tracker_file):
        try:
            with open(tracker_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            log_message("ERROR", f"Error reading version file {tracker_file}: {e}")
    return None

def get_current_byte_size(filename):
    """Get current stored byte size"""
    tracker_file = get_byte_tracker_path(filename)
    if os.path.exists(tracker_file):
        try:
            with open(tracker_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except Exception as e:
            log_message("ERROR", f"Error reading byte file {tracker_file}: {e}")
    return None

def get_current_content_hash(filename):
    """Get current stored content hash"""
    tracker_file = get_hash_tracker_path(filename)
    if os.path.exists(tracker_file):
        try:
            with open(tracker_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            log_message("ERROR", f"Error reading hash file {tracker_file}: {e}")
    return None

def save_current_version(filename, content_sha):
    """Save current version (content SHA)"""
    tracker_file = get_version_tracker_path(filename)
    try:
        with open(tracker_file, 'w', encoding='utf-8') as f:
            f.write(content_sha)
        log_message("DEBUG", f"Saved version {content_sha[:8]} for {filename}")
        return True
    except Exception as e:
        log_message("ERROR", f"Failed to save version for {filename}: {e}", send_to_discord=True)
        return False

def save_current_byte_size(filename, byte_size):
    """Save current byte size"""
    tracker_file = get_byte_tracker_path(filename)
    try:
        with open(tracker_file, 'w', encoding='utf-8') as f:
            f.write(str(byte_size))
        log_message("DEBUG", f"Saved byte size {byte_size} for {filename}")
        return True
    except Exception as e:
        log_message("ERROR", f"Failed to save byte size for {filename}: {e}")
        return False

def save_current_content_hash(filename, content_hash):
    """Save current content hash"""
    tracker_file = get_hash_tracker_path(filename)
    try:
        with open(tracker_file, 'w', encoding='utf-8') as f:
            f.write(content_hash)
        log_message("DEBUG", f"Saved content hash {content_hash[:8]} for {filename}")
        return True
    except Exception as e:
        log_message("ERROR", f"Failed to save content hash for {filename}: {e}")
        return False

def optimized_webhook_worker():
    """Optimized worker thread to send webhook messages with batching"""
    config = load_config()
    batch_size = 5  # Process up to 5 webhooks at once
    max_wait_time = 30  # Maximum time to wait before processing batch
    
    while not shutdown_event.is_set():
        try:
            # Wait for first item with timeout
            try:
                webhook_url, payload = webhook_queue.get(timeout=max_wait_time)
            except queue.Empty:
                continue  # Timeout reached, check shutdown event
            
            if webhook_url is None:  # Sentinel to stop worker
                break
                
            # Try to process a batch of items
            webhooks_to_process = [(webhook_url, payload)]
            
            # Get additional items without waiting
            for _ in range(batch_size - 1):
                try:
                    item = webhook_queue.get_nowait()
                    if item[0] is None:  # Check for sentinel
                        break
                    webhooks_to_process.append(item)
                except queue.Empty:
                    break
            
            # Process the batch
            for wh_url, wh_payload in webhooks_to_process:
                max_retries = 2  # Reduced from 3
                for attempt in range(max_retries):
                    try:
                        data = json.dumps(wh_payload).encode('utf-8')
                        req = urllib.request.Request(
                            wh_url,
                            data=data,
                            headers={'Content-Type': 'application/json', 'User-Agent': 'GitHubLauncher/1.0'}
                        )
                        response = urllib.request.urlopen(req, timeout=15)  # Increased timeout
                        if response.status == 204:
                            log_message("DEBUG", f"Webhook sent to {wh_url[:30]}...")
                            break
                    except urllib.error.HTTPError as e:
                        if e.code == 429:  # Rate limited
                            retry_after = e.headers.get('Retry-After', 10)
                            time.sleep(float(retry_after))
                        elif e.code >= 500:
                            time.sleep(2 ** attempt)  # Exponential backoff for server errors
                        else:
                            break  # Client errors, don't retry
                    except Exception:
                        time.sleep(1)  # Short sleep on network errors
                
                webhook_queue.task_done()
                
        except Exception as e:
            log_message("ERROR", f"Webhook worker error: {e}")
            time.sleep(5)

def send_discord_notification(title, description, level="info", error_details=None, script_output=None, additional_script_output=None):
    """Send a notification to Discord webhooks"""
    config = load_config()
    
    # Check if Discord logging is enabled
    if not config.get('enable_discord_logging', True):
        return
    
    # Colors for different levels
    colors = {
        "info": 3447003,      # Blue
        "success": 3066993,   # Green
        "warning": 16776960,  # Yellow
        "error": 15158332,    # Red
        "critical": 10038562, # Dark Red
        "startup": 10181046   # Purple
    }
    
    color = colors.get(level.lower(), colors["info"])
    
    # Prepare the embed
    embed = {
        "title": title,
        "description": description[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": f"GitHub Launcher v2.0 • {level.upper()}"
        },
        "fields": []
    }
    
    # Add error details if provided
    if error_details:
        if isinstance(error_details, str):
            error_text = error_details[:1000]
            if len(error_details) > 1000:
                error_text += "... (truncated)"
            embed["fields"].append({
                "name": "📝 Error Details",
                "value": f"```{error_text}```",
                "inline": False
            })
    
    # Add main script output if available
    if script_output:
        output_text = script_output[:1000]
        if len(script_output) > 1000:
            output_text = "... (truncated)\n" + script_output[-1000:]
        embed["fields"].append({
            "name": "📊 Main Script Output",
            "value": f"```{output_text}```",
            "inline": False
        })
    
    # Add additional script output if available
    if additional_script_output:
        output_text = additional_script_output[:1000]
        if len(additional_script_output) > 1000:
            output_text = "... (truncated)\n" + additional_script_output[-1000:]
        embed["fields"].append({
            "name": "📊 Additional Script Output",
            "value": f"```{output_text}```",
            "inline": False
        })
    
    # Add system info
    try:
        cpu_info = get_cpu_usage()
        embed["fields"].append({
            "name": "🖥️ System Info",
            "value": f"CPU: {cpu_info['cpu_percent']}%\nMemory: {cpu_info['memory_mb']}MB\nThreads: {cpu_info['threads']}",
            "inline": True
        })
    except:
        pass
    
    # Prepare the payload
    payload = {
        "embeds": [embed],
        "username": "GitHub Launcher",
        "avatar_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
    }
    
    # Send to all webhooks via queue
    for webhook_url in config.get('discord_webhooks', []):
        if webhook_url:
            webhook_queue.put((webhook_url, payload))

def log_message(level, message, send_to_discord=False, error_details=None, include_output=False, script_type="main"):
    """Log messages with optional Discord notification"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_line = f"[{timestamp}] [{level}] [{script_type.upper()}] {message}"
    print(log_line)
    
    # Store in appropriate output buffer
    if script_type == "main":
        buffer = script_output_buffer
    else:
        buffer = additional_script_output_buffer
    
    if len(buffer) >= MAX_OUTPUT_BUFFER:
        buffer.pop(0)
    buffer.append(log_line)
    
    # Send to Discord if requested
    if send_to_discord:
        discord_level = level.lower()
        
        # Get outputs for both scripts
        main_output = None
        additional_output = None
        
        if include_output:
            if script_type == "main" and script_output_buffer:
                main_output = "\n".join(script_output_buffer[-10:])
                if additional_script_output_buffer:
                    additional_output = "\n".join(additional_script_output_buffer[-5:])
            elif script_type == "additional" and additional_script_output_buffer:
                additional_output = "\n".join(additional_script_output_buffer[-10:])
                if script_output_buffer:
                    main_output = "\n".join(script_output_buffer[-5:])
        
        send_discord_notification(
            f"[{level.upper()}] [{script_type.upper()}] {message[:100]}",
            message,
            discord_level,
            error_details,
            main_output,
            additional_output
        )

def check_rate_limit():
    """Check if we need to wait due to rate limiting"""
    global rate_limit_wait
    
    if rate_limit_wait > 0:
        wait_time = rate_limit_wait
        rate_limit_wait = 0
        log_message("WARNING", f"Rate limited, waiting {wait_time} seconds", send_to_discord=True)
        time.sleep(wait_time)
        return True
    return False

def make_github_request(url, headers=None, retry_count=0):
    """Make a GitHub API request with rate limit handling"""
    global rate_limit_wait
    
    if retry_count >= 2:  # Reduced from 3
        log_message("ERROR", f"Max retries exceeded for {url}", send_to_discord=True)
        return None
    
    # Check if we need to wait due to rate limiting
    if check_rate_limit():
        retry_count += 1
        return make_github_request(url, headers, retry_count)
    
    try:
        if headers is None:
            headers = {}
        
        config = load_config()
        token = config.get('github_token')
        
        if token:
            headers['Authorization'] = f"token {token}"
        
        headers['User-Agent'] = 'GitHubLauncher/2.0'
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)  # Increased timeout
        return response
        
    except urllib.error.HTTPError as e:
        if e.code == 403:
            # Rate limited
            reset_time = int(e.headers.get('X-RateLimit-Reset', 0))
            current_time = int(time.time())
            
            if reset_time > current_time:
                wait_time = reset_time - current_time + 1
                rate_limit_wait = wait_time
                log_message("WARNING", f"Rate limited. Reset in {wait_time} seconds", send_to_discord=True)
            else:
                rate_limit_wait = 60
            
            # Retry after waiting
            time.sleep(rate_limit_wait)
            return make_github_request(url, headers, retry_count + 1)
        elif e.code == 404:
            log_message("ERROR", f"File not found: {url}", send_to_discord=True)
            return None
        else:
            log_message("ERROR", f"HTTP error {e.code}: {e.reason}", send_to_discord=True)
            return None
    except Exception as e:
        log_message("ERROR", f"Request failed: {e}", send_to_discord=True)
        return None

def get_file_info(file_path):
    """Get file information including SHA and size from GitHub API"""
    config = load_config()
    
    api_url = f"https://api.github.com/repos/{config['repository_owner']}/{config['repository_name']}/contents/{urllib.parse.quote(file_path)}"
    params = {
        'ref': config['branch']
    }
    
    query = urllib.parse.urlencode(params)
    url = f"{api_url}?{query}"
    
    try:
        response = make_github_request(url)
        if response:
            file_info = json.loads(response.read().decode('utf-8'))
            if 'sha' in file_info and 'size' in file_info:
                return {
                    'sha': file_info['sha'],
                    'size': file_info['size'],
                    'name': file_info.get('name', ''),
                    'content': file_info.get('content', ''),  # Base64 encoded content
                    'encoding': file_info.get('encoding', '')
                }
        return None
        
    except Exception as e:
        log_message("ERROR", f"Failed to get file info for {file_path}: {e}", send_to_discord=True)
        return None

def verify_byte_size_change(file_path, new_sha, new_size):
    """Verify that byte size has actually changed from previous version"""
    config = load_config()
    
    if not config.get('enable_byte_verification', True):
        return True  # Skip verification if disabled
    
    # Get stored byte size
    current_size = get_current_byte_size(file_path)
    
    if current_size is None:
        # No previous size stored, treat as changed
        log_message("INFO", f"No previous byte size stored for {file_path}, accepting new size: {new_size} bytes")
        return True
    
    if current_size != new_size:
        # Byte size has changed
        log_message("INFO", f"Byte size changed for {file_path}: {current_size} -> {new_size} bytes")
        return True
    else:
        # Byte size hasn't changed, but SHA has
        log_message("WARNING", f"SHA changed but byte size unchanged for {file_path}: {new_size} bytes", send_to_discord=True)
        
        # Check if we should retry
        retries = config.get('byte_verification_retries', 3)
        delay = config.get('byte_verification_delay', 10)
        
        for attempt in range(retries):
            log_message("INFO", f"Byte verification attempt {attempt + 1}/{retries} for {file_path}")
            time.sleep(delay)
            
            # Re-fetch file info
            refreshed_info = get_file_info(file_path)
            if refreshed_info and refreshed_info['sha'] == new_sha:
                # SHA still the same, check size again
                if refreshed_info['size'] != new_size:
                    # Size has changed on retry
                    log_message("INFO", f"Byte size changed on retry {attempt + 1}: {new_size} -> {refreshed_info['size']} bytes")
                    return True
                else:
                    log_message("INFO", f"Byte size still unchanged on retry {attempt + 1}: {refreshed_info['size']} bytes")
            else:
                # SHA changed during retry
                log_message("INFO", f"SHA changed during byte verification retry for {file_path}")
                return False  # SHA changed, will be handled in next check cycle
        
        # All retries failed
        log_message("ERROR", f"Byte size verification failed after {retries} retries for {file_path}. Not executing update.", send_to_discord=True)
        return False

def check_for_updates():
    """Check for updates using GitHub API with byte size verification"""
    global last_update_check, update_check_count
    current_time = time.time()
    
    config = load_config()
    update_interval = config.get('update_check_interval', 300)
    min_interval = config.get('min_update_interval', 30)
    
    # Use the larger of the two intervals
    effective_interval = max(update_interval, min_interval)
    
    # Check minimum effective interval
    if current_time - last_update_check < effective_interval:
        return []
    
    last_update_check = current_time
    update_check_count += 1
    updated_files = []
    
    try:
        # Check main script
        script_info = get_file_info(config['script_path'])
        if script_info:
            script_content_sha = script_info['sha']
            script_size = script_info['size']
            current_sha = get_current_version("script")
            if current_sha:
                if script_content_sha != current_sha:
                    # Verify byte size has also changed
                    if verify_byte_size_change("script", script_content_sha, script_size):
                        log_message("INFO", f"script.py updated (SHA: {script_content_sha[:8]}, Size: {script_size} bytes)", 
                                   send_to_discord=True, script_type="main")
                        updated_files.append("script")
                        # Save new byte size
                        save_current_byte_size("script", script_size)
                    else:
                        log_message("WARNING", f"script.py SHA changed but byte size verification failed. Update deferred.", 
                                   send_to_discord=True, script_type="main")
        
        # Check additional script
        additional_script_path = config.get('additional_script_path')
        if additional_script_path:
            additional_info = get_file_info(additional_script_path)
            if additional_info:
                additional_content_sha = additional_info['sha']
                additional_size = additional_info['size']
                current_sha = get_current_version("additional")
                if current_sha:
                    if additional_content_sha != current_sha:
                        # Verify byte size has also changed
                        if verify_byte_size_change("additional", additional_content_sha, additional_size):
                            log_message("INFO", f"additional.pyw updated (SHA: {additional_content_sha[:8]}, Size: {additional_size} bytes)", 
                                       send_to_discord=True, script_type="additional")
                            updated_files.append("additional")
                            # Save new byte size
                            save_current_byte_size("additional", additional_size)
                        else:
                            log_message("WARNING", f"additional.pyw SHA changed but byte size verification failed. Update deferred.", 
                                       send_to_discord=True, script_type="additional")
        
        # Check requirements
        requirements_info = get_file_info(config['requirements_path'])
        if requirements_info:
            requirements_content_sha = requirements_info['sha']
            requirements_size = requirements_info['size']
            current_sha = get_current_version("requirements")
            if current_sha:
                if requirements_content_sha != current_sha:
                    # Verify byte size has also changed
                    if verify_byte_size_change("requirements", requirements_content_sha, requirements_size):
                        log_message("INFO", f"requirements.txt updated (SHA: {requirements_content_sha[:8]}, Size: {requirements_size} bytes)", 
                                   send_to_discord=True)
                        updated_files.append("requirements")
                        # Save new byte size
                        save_current_byte_size("requirements", requirements_size)
                    else:
                        log_message("WARNING", f"requirements.txt SHA changed but byte size verification failed. Update deferred.", 
                                   send_to_discord=True)
        
        return updated_files
        
    except Exception as e:
        log_message("ERROR", f"Error checking for updates: {e}", send_to_discord=True)
        return []

def download_file_with_cache_control(file_path):
    """Download file with cache control to avoid CDN issues"""
    config = load_config()
    
    # Use the GitHub API to get base64 encoded content (more reliable than raw URL)
    file_info = get_file_info(file_path)
    if file_info and 'content' in file_info and file_info['encoding'] == 'base64':
        try:
            # Decode base64 content
            content = base64.b64decode(file_info['content']).decode('utf-8')
            
            # Verify downloaded content size
            downloaded_size = len(content.encode('utf-8'))
            expected_size = file_info['size']
            
            if downloaded_size != expected_size:
                log_message("WARNING", f"API content size mismatch for {file_path}: expected {expected_size}, got {downloaded_size} bytes")
                # Try fallback to raw URL
                return download_file_direct_fallback(file_path, expected_size)
            
            return content
        except Exception as e:
            log_message("ERROR", f"Failed to decode base64 content for {file_path}: {e}")
            # Fallback to raw URL
            return download_file_direct_fallback(file_path)
    
    # Fallback to raw URL if API doesn't return content
    return download_file_direct_fallback(file_path)

def download_file_direct_fallback(file_path, expected_size=None):
    """Fallback download using raw URL with cache control"""
    config = load_config()
    
    raw_url = f"https://raw.githubusercontent.com/{config['repository_owner']}/{config['repository_name']}/{config['branch']}/{urllib.parse.quote(file_path)}"
    
    # Add cache-busting parameter if enabled
    if config.get('cache_busting', True):
        cache_buster = str(int(time.time() * 1000))
        raw_url = f"{raw_url}?cb={cache_buster}"
    
    try:
        headers = {'User-Agent': 'GitHubLauncher/2.0'}
        
        # Add cache control headers if enabled
        if config.get('enable_cache_control', True):
            headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            headers['Pragma'] = 'no-cache'
            headers['Expires'] = '0'
        
        token = config.get('github_token')
        if token:
            headers['Authorization'] = f"token {token}"
        
        req = urllib.request.Request(raw_url, headers=headers)
        response = urllib.request.urlopen(req, timeout=15)
        content = response.read().decode('utf-8')
        
        # Verify downloaded content size matches expected
        downloaded_size = len(content.encode('utf-8'))
        if expected_size and downloaded_size != expected_size:
            log_message("WARNING", f"Downloaded size mismatch for {file_path}: expected {expected_size}, got {downloaded_size} bytes")
            # Still return the content, but log the warning
        
        return content
        
    except Exception as e:
        log_message("ERROR", f"Failed to download {file_path}: {e}", send_to_discord=True)
        return None

def calculate_content_hash(content):
    """Calculate SHA256 hash of content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def verify_downloaded_content(file_type, content, expected_size, remote_sha):
    """Verify downloaded content matches expectations"""
    if not content:
        return False, "No content downloaded"
    
    # Check size
    downloaded_size = len(content.encode('utf-8'))
    if expected_size and downloaded_size != expected_size:
        return False, f"Size mismatch: expected {expected_size}, got {downloaded_size} bytes"
    
    # Calculate hash of downloaded content
    content_hash = calculate_content_hash(content)
    
    # Get previous hash for comparison
    previous_hash = get_current_content_hash(file_type)
    
    if previous_hash and content_hash == previous_hash:
        # Content hash hasn't changed even though SHA and size changed
        log_message("WARNING", f"Content hash unchanged for {file_type} (hash: {content_hash[:8]})")
        
        # Double-check by downloading again with different method
        config = load_config()
        file_path = ""
        if file_type == "script":
            file_path = config['script_path']
        elif file_type == "additional":
            file_path = config.get('additional_script_path', '')
        elif file_type == "requirements":
            file_path = config['requirements_path']
        
        if file_path:
            # Try alternative download method
            alt_content = download_file_direct_fallback(file_path)
            if alt_content:
                alt_hash = calculate_content_hash(alt_content)
                if alt_hash != content_hash:
                    log_message("INFO", f"Alternative download yielded different hash: {alt_hash[:8]} vs {content_hash[:8]}")
                    return True, "Content verified (alternative download different)"
    
    return True, f"Content verified (size: {downloaded_size} bytes, hash: {content_hash[:8]})"

def optimized_capture_script_output(process, script_type="main"):
    """Optimized: Capture and log script output in real-time"""
    def read_stream(stream, stream_name):
        try:
            # Use non-blocking read to reduce CPU usage
            import fcntl
            import os
            # Set non-blocking mode
            fl = fcntl.fcntl(stream.fileno(), fcntl.F_GETFL)
            fcntl.fcntl(stream.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
            
            buffer = ""
            while not shutdown_event.is_set():
                try:
                    chunk = stream.read(1024)
                    if chunk:
                        buffer += chunk
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.rstrip()
                            if line:
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                log_line = f"[{timestamp}] [{script_type.upper()}-{stream_name}] {line}"
                                
                                # Store in appropriate buffer
                                if script_type == "main":
                                    target_buffer = script_output_buffer
                                else:
                                    target_buffer = additional_script_output_buffer
                                
                                if len(target_buffer) >= MAX_OUTPUT_BUFFER:
                                    target_buffer.pop(0)
                                target_buffer.append(log_line)
                                
                                # Print to console
                                print(log_line)
                    else:
                        # No data available, sleep
                        time.sleep(0.1)
                except (IOError, OSError):
                    # No data available, sleep
                    time.sleep(0.1)
                except Exception as e:
                    log_message("ERROR", f"Error reading {script_type} {stream_name}: {e}", 
                               send_to_discord=False, script_type=script_type)
                    time.sleep(1)
        except ImportError:
            # Fallback for Windows without fcntl
            while not shutdown_event.is_set():
                try:
                    line = stream.readline()
                    if line:
                        line = line.rstrip()
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        log_line = f"[{timestamp}] [{script_type.upper()}-{stream_name}] {line}"
                        
                        if script_type == "main":
                            target_buffer = script_output_buffer
                        else:
                            target_buffer = additional_script_output_buffer
                        
                        if len(target_buffer) >= MAX_OUTPUT_BUFFER:
                            target_buffer.pop(0)
                        target_buffer.append(log_line)
                        
                        print(log_line)
                    else:
                        # Check if process is still alive
                        if process.poll() is not None:
                            break
                        time.sleep(0.5)
                except Exception as e:
                    log_message("ERROR", f"Error reading {script_type} {stream_name}: {e}", 
                               send_to_discord=False, script_type=script_type)
                    time.sleep(1)
        except Exception as e:
            log_message("ERROR", f"Error in stream reader: {e}", send_to_discord=False, script_type=script_type)
    
    # Start output readers
    stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, "STDOUT"), daemon=True)
    stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, "STDERR"), daemon=True)
    
    stdout_thread.start()
    stderr_thread.start()

def run_additional_script():
    """Download and run additional.pyw - handles empty files gracefully"""
    global current_additional_script_process
    
    config = load_config()
    additional_script_path = config.get('additional_script_path')
    
    if not additional_script_path:
        log_message("INFO", "No additional script configured", send_to_discord=False, script_type="additional")
        return True
    
    temp_script = None
    
    try:
        # Get current file info to check if we need to update
        remote_info = get_file_info(additional_script_path)
        
        # If file doesn't exist on GitHub, just return success (no error)
        if not remote_info:
            log_message("INFO", "Additional script not found on GitHub (file may not exist)", 
                       send_to_discord=False, script_type="additional")
            return True
        
        remote_sha = remote_info['sha']
        remote_size = remote_info['size']
        
        # Get current stored SHA
        current_sha = get_current_version("additional")
        
        # Check if we need to update (either different SHA or no SHA stored)
        need_to_update = False
        if current_sha != remote_sha:
            need_to_update = True
            log_message("INFO", f"Additional script update detected (SHA: {remote_sha[:8]}, Size: {remote_size} bytes)", 
                       send_to_discord=True, script_type="additional")
        
        # If we already have the latest version and script is running, don't restart
        if not need_to_update and current_additional_script_process and current_additional_script_process.poll() is None:
            log_message("DEBUG", "Additional script is already up to date and running", 
                       send_to_discord=False, script_type="additional")
            return True
        
        # Download script with cache control
        script_content = download_file_with_cache_control(additional_script_path)
        
        # Check if script is empty or doesn't exist
        if not script_content:
            log_message("INFO", "Additional script is empty or not accessible", 
                       send_to_discord=False, script_type="additional")
            save_current_version("additional", remote_sha)
            save_current_byte_size("additional", remote_size)
            return True
        
        # Check if script content is empty after stripping whitespace
        if script_content.strip() == "":
            log_message("INFO", "Additional script is empty (0 bytes), skipping execution", 
                       send_to_discord=False, script_type="additional")
            save_current_version("additional", remote_sha)
            save_current_byte_size("additional", remote_size)
            return True
        
        # Verify downloaded content
        verified, verification_msg = verify_downloaded_content("additional", script_content, remote_size, remote_sha)
        if not verified:
            log_message("ERROR", f"Content verification failed for additional script: {verification_msg}", 
                       send_to_discord=True, script_type="additional")
            return False
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))
        temp_script = os.path.join(temp_dir, f"additional_{timestamp}.pyw")
        
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Verify temp file size matches expected
        temp_size = os.path.getsize(temp_script)
        if temp_size != remote_size:
            log_message("WARNING", f"Temp file size mismatch: expected {remote_size}, got {temp_size} bytes", 
                       send_to_discord=True, script_type="additional")
        
        log_message("INFO", f"Additional script saved to: {temp_script} ({temp_size} bytes, {verification_msg})", 
                   send_to_discord=False, script_type="additional")
        
        # Terminate existing additional script process if any
        if current_additional_script_process:
            if current_additional_script_process.poll() is None:
                log_message("INFO", "Terminating previous additional script instance", 
                           send_to_discord=True, script_type="additional")
                try:
                    current_additional_script_process.terminate()
                    try:
                        current_additional_script_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        current_additional_script_process.kill()
                        current_additional_script_process.wait()
                except Exception as e:
                    log_message("ERROR", f"Error terminating previous additional script: {e}", 
                               send_to_discord=True, script_type="additional")
        
        # Run it hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        script_ext = os.path.splitext(additional_script_path)[1].lower()
        if script_ext == '.pyw':
            pythonw_exe = sys.executable.replace('python.exe', 'pythonw.exe')
            if os.path.exists(pythonw_exe):
                executable = pythonw_exe
                creation_flags = 0
            else:
                executable = sys.executable
                creation_flags = subprocess.CREATE_NO_WINDOW
        else:
            executable = sys.executable
            creation_flags = subprocess.CREATE_NO_WINDOW
        
        process = subprocess.Popen(
            [executable, temp_script],
            startupinfo=startupinfo,
            creationflags=creation_flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8'
        )
        
        current_additional_script_process = process
        
        # Start capturing output
        optimized_capture_script_output(process, "additional")
        
        # Check if process starts
        time.sleep(2)
        
        if process.poll() is not None:
            stderr_output = ""
            try:
                stdout, stderr = process.communicate(timeout=2)
                if stderr:
                    stderr_output = stderr[:500]
            except:
                pass
            
            if process.returncode == 0:
                log_message("INFO", "Additional script completed successfully (exit code 0)", 
                           send_to_discord=False, script_type="additional")
                save_current_version("additional", remote_sha)
                save_current_byte_size("additional", remote_size)
                save_current_content_hash("additional", calculate_content_hash(script_content))
                return True
            else:
                error_msg = f"Additional script terminated with code: {process.returncode}"
                log_message("ERROR", error_msg, send_to_discord=True, 
                           error_details=stderr_output, include_output=True, script_type="additional")
                return False
        
        # Script is still running
        success_msg = f"Additional script started successfully! PID: {process.pid} SHA: {remote_sha[:8]} Size: {remote_size} bytes"
        log_message("SUCCESS", success_msg, send_to_discord=True, include_output=True, script_type="additional")
        
        save_current_version("additional", remote_sha)
        save_current_byte_size("additional", remote_size)
        save_current_content_hash("additional", calculate_content_hash(script_content))
        
        # Clean up temp file
        def cleanup_temp():
            time.sleep(30)
            try:
                if os.path.exists(temp_script):
                    os.remove(temp_script)
            except:
                pass
        
        threading.Thread(target=cleanup_temp, daemon=True).start()
        
        return True
        
    except Exception as e:
        error_msg = f"Error running additional script: {e}"
        error_details = traceback.format_exc()
        
        if "404" in str(e) or "empty" in str(e).lower() or "not found" in str(e).lower():
            log_message("INFO", f"Additional script not available: {e}", 
                       send_to_discord=False, script_type="additional")
            return True
        
        log_message("ERROR", error_msg, send_to_discord=True, 
                   error_details=error_details, include_output=True, script_type="additional")
        
        if temp_script and os.path.exists(temp_script):
            try:
                os.remove(temp_script)
            except:
                pass
        
        return False

def run_script_from_github():
    """Download and run script.py"""
    global current_script_process
    
    config = load_config()
    temp_script = None
    
    try:
        # Get current file info to check if we need to update
        remote_info = get_file_info(config['script_path'])
        
        if not remote_info:
            error_msg = "Failed to get remote script info"
            log_message("ERROR", error_msg, send_to_discord=True, script_type="main")
            return False
        
        remote_sha = remote_info['sha']
        remote_size = remote_info['size']
        
        # Get current stored SHA
        current_sha = get_current_version("script")
        
        # If we already have the latest version and script is running, don't restart
        if current_sha == remote_sha and current_script_process and current_script_process.poll() is None:
            log_message("INFO", "Script is already up to date and running", script_type="main")
            return True
        
        # Download script with cache control
        script_content = download_file_with_cache_control(config['script_path'])
        
        if not script_content:
            error_msg = "Failed to download script"
            log_message("ERROR", error_msg, send_to_discord=True, script_type="main")
            return False
        
        # Verify downloaded content
        verified, verification_msg = verify_downloaded_content("script", script_content, remote_size, remote_sha)
        if not verified:
            log_message("ERROR", f"Content verification failed for main script: {verification_msg}", 
                       send_to_discord=True, script_type="main")
            return False
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))
        temp_script = os.path.join(temp_dir, f"script_{timestamp}.py")
        
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Verify temp file size matches expected
        temp_size = os.path.getsize(temp_script)
        if temp_size != remote_size:
            log_message("WARNING", f"Temp file size mismatch: expected {remote_size}, got {temp_size} bytes", 
                       send_to_discord=True, script_type="main")
        
        log_message("INFO", f"Script saved to: {temp_script} ({temp_size} bytes, {verification_msg})", script_type="main")
        
        # Terminate existing script process if any
        if current_script_process and current_script_process.poll() is None:
            log_message("INFO", "Terminating previous script instance", send_to_discord=True, script_type="main")
            try:
                current_script_process.terminate()
                try:
                    current_script_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    current_script_process.kill()
                    current_script_process.wait()
            except:
                pass
        
        # Run it hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, temp_script],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        current_script_process = process
        
        # Start capturing output
        optimized_capture_script_output(process, "main")
        
        # Check if process starts
        time.sleep(2)
        
        if process.poll() is not None:
            stderr_output = ""
            try:
                stdout, stderr = process.communicate(timeout=2)
                if stderr:
                    stderr_output = stderr[:500]
            except:
                pass
            
            error_msg = f"Script terminated immediately with code: {process.returncode}"
            log_message("ERROR", error_msg, send_to_discord=True, error_details=stderr_output, include_output=True, script_type="main")
            return False
        
        # Send startup success notification
        success_msg = f"✅ Main script started successfully!\nPID: {process.pid}\nSHA: {remote_sha[:8]}\nSize: {remote_size} bytes\nVerification: {verification_msg}"
        log_message("SUCCESS", success_msg, send_to_discord=True, include_output=True, script_type="main")
        
        # Save content SHA, byte size, and content hash after successful start
        save_current_version("script", remote_sha)
        save_current_byte_size("script", remote_size)
        save_current_content_hash("script", calculate_content_hash(script_content))
        
        # Clean up temp file after delay
        def cleanup_temp():
            time.sleep(30)
            try:
                if os.path.exists(temp_script):
                    os.remove(temp_script)
                    log_message("DEBUG", "Temp file cleaned up", script_type="main")
            except:
                pass
        
        threading.Thread(target=cleanup_temp, daemon=True).start()
        
        return True
        
    except Exception as e:
        error_msg = f"Error running script: {e}"
        log_message("ERROR", error_msg, send_to_discord=True, error_details=traceback.format_exc(), include_output=True, script_type="main")
        if temp_script and os.path.exists(temp_script):
            try:
                os.remove(temp_script)
            except:
                pass
        return False

def install_requirements():
    """Download and install requirements"""
    config = load_config()
    
    try:
        # Get current info to check if we need to update
        remote_info = get_file_info(config['requirements_path'])
        
        if not remote_info:
            log_message("INFO", "No requirements.txt found or can't access")
            return True
        
        remote_sha = remote_info['sha']
        remote_size = remote_info['size']
        
        # Get current stored SHA
        current_sha = get_current_version("requirements")
        
        # Check if we need to install
        if current_sha == remote_sha:
            log_message("INFO", "Requirements already up to date")
            return True
        
        # Download requirements with cache control
        requirements_content = download_file_with_cache_control(config['requirements_path'])
        
        if not requirements_content:
            log_message("INFO", "No requirements.txt or empty")
            save_current_version("requirements", remote_sha)
            save_current_byte_size("requirements", remote_size)
            return True
        
        if not requirements_content.strip():
            log_message("INFO", "Empty requirements.txt")
            save_current_version("requirements", remote_sha)
            save_current_byte_size("requirements", remote_size)
            return True
        
        # Validate requirements file content
        lines = requirements_content.strip().split('\n')
        valid_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                valid_lines.append(line)
        
        if not valid_lines:
            log_message("INFO", "No valid requirements found")
            save_current_version("requirements", remote_sha)
            save_current_byte_size("requirements", remote_size)
            return True
        
        # Install requirements
        log_message("INFO", f"Installing {len(valid_lines)} requirements...", send_to_discord=True)
        
        # Save requirements to temp file
        temp_dir = tempfile.gettempdir()
        temp_req = os.path.join(temp_dir, f"requirements_{int(time.time())}.txt")
        
        with open(temp_req, 'w', encoding='utf-8') as f:
            f.write('\n'.join(valid_lines))
        
        # Run pip install
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "-r", temp_req, "--quiet"],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        process.wait(timeout=120)
        
        if process.returncode == 0:
            success_msg = f"✅ Successfully installed {len(valid_lines)} requirements"
            log_message("SUCCESS", success_msg, send_to_discord=True)
            save_current_version("requirements", remote_sha)
            save_current_byte_size("requirements", remote_size)
            save_current_content_hash("requirements", calculate_content_hash(requirements_content))
        else:
            stdout, stderr = process.communicate()
            error_details = ""
            if stderr:
                error_details = stderr.decode('utf-8')[:500]
                log_message("ERROR", f"Pip error: {error_details}")
            error_msg = f"Failed to install requirements: {process.returncode}"
            log_message("ERROR", error_msg, send_to_discord=True, error_details=error_details)
        
        # Clean up
        try:
            os.remove(temp_req)
        except:
            pass
        
        return process.returncode == 0
        
    except Exception as e:
        error_msg = f"Error installing requirements: {e}"
        log_message("ERROR", error_msg, send_to_discord=True, error_details=traceback.format_exc())
        return False

def initial_setup():
    """Perform initial setup - called once at startup"""
    global initial_setup_complete
    
    if initial_setup_complete:
        return
    
    log_message("STARTUP", "🚀 Performing initial setup...", send_to_discord=True)
    
    # Get SHAs and byte sizes and save them without triggering updates
    config = load_config()
    
    for file_path, file_type in [(config['script_path'], "script"), 
                                 (config.get('additional_script_path', ''), "additional"),
                                 (config['requirements_path'], "requirements")]:
        if file_path:
            file_info = get_file_info(file_path)
            if file_info:
                current_sha = get_current_version(file_type)
                if not current_sha:
                    save_current_version(file_type, file_info['sha'])
                    save_current_byte_size(file_type, file_info['size'])
    
    # Install requirements
    log_message("INFO", "Checking requirements...", send_to_discord=True)
    if not install_requirements():
        log_message("WARNING", "Requirements check had issues", send_to_discord=True)
    
    # Start main script
    log_message("INFO", "Starting main script...", send_to_discord=True)
    time.sleep(2)
    if not run_script_from_github():
        log_message("ERROR", "Failed to start main script during initial setup", 
                   send_to_discord=True, include_output=True, script_type="main")
    
    # Start additional script if configured
    if config.get('additional_script_path'):
        log_message("INFO", "Checking additional script...", send_to_discord=False, script_type="additional")
        time.sleep(2)
        
        result = run_additional_script()
        
        if not result:
            if current_additional_script_process and current_additional_script_process.returncode != 0:
                log_message("ERROR", "Additional script failed to start", 
                           send_to_discord=True, include_output=True, script_type="additional")
    
    initial_setup_complete = True

def optimized_monitor_updates():
    """Optimized: Monitor for updates with proper sleeping"""
    
    # Do initial setup first
    initial_setup()
    
    config = load_config()
    cpu_monitor_interval = config.get('cpu_monitor_interval', 60)
    last_cpu_check = 0
    
    while not shutdown_event.is_set():
        try:
            current_time = time.time()
            
            # Check CPU usage periodically
            if current_time - last_cpu_check >= cpu_monitor_interval:
                cpu_info = get_cpu_usage()
                if cpu_info['cpu_percent'] > config.get('max_cpu_percent', 5.0):
                    log_message("WARNING", f"High CPU usage detected: {cpu_info['cpu_percent']}%", 
                               send_to_discord=True)
                last_cpu_check = current_time
            
            # Clear rate limit wait at the start of each check
            global rate_limit_wait
            rate_limit_wait = 0
            
            log_message("INFO", f"Checking for updates...")
            
            # Check for actual updates
            updated_files = check_for_updates()
            
            if updated_files:
                update_msg = f"Updates detected: {', '.join(updated_files)}"
                log_message("INFO", update_msg, send_to_discord=True, include_output=True)
                
                # Handle requirements first if needed
                if "requirements" in updated_files:
                    if install_requirements():
                        time.sleep(5)
                
                # Handle main script update
                if "script" in updated_files:
                    run_script_from_github()
                
                # Handle additional script update
                if "additional" in updated_files:
                    log_message("INFO", "Updating additional script...", 
                               send_to_discord=True, script_type="additional")
                    result = run_additional_script()
                    if not result:
                        if current_additional_script_process and current_additional_script_process.returncode != 0:
                            log_message("WARNING", "Additional script update failed", 
                                       send_to_discord=True, include_output=True, script_type="additional")
            
            # Check if scripts are still running
            # Main script
            if current_script_process:
                if current_script_process.poll() is not None:
                    warning_msg = f"Main script has stopped (Code: {current_script_process.returncode}), attempting to restart..."
                    log_message("WARNING", warning_msg, send_to_discord=True, include_output=True, script_type="main")
                    if not run_script_from_github():
                        error_msg = "Failed to restart main script"
                        log_message("ERROR", error_msg, send_to_discord=True, include_output=True, script_type="main")
            
            # Additional script
            if current_additional_script_process:
                if current_additional_script_process.poll() is not None:
                    if current_additional_script_process.returncode != 0:
                        warning_msg = f"Additional script has stopped (Code: {current_additional_script_process.returncode}), attempting to restart..."
                        log_message("WARNING", warning_msg, send_to_discord=True, include_output=True, script_type="additional")
                        if not run_additional_script():
                            error_msg = "Failed to restart additional script"
                            log_message("ERROR", error_msg, send_to_discord=True, include_output=True, script_type="additional")
                    else:
                        log_message("INFO", "Additional script completed normally (exit code 0)", 
                                   send_to_discord=False, script_type="additional")
            
        except Exception as e:
            error_msg = f"Error in update monitor: {e}"
            log_message("ERROR", error_msg, send_to_discord=True, error_details=traceback.format_exc())
        
        # Sleep for the configured interval
        try:
            config = load_config()
            update_interval = config.get('update_check_interval', 300)
            min_interval = config.get('min_update_interval', 30)
            
            # Use the larger of the two intervals for sleeping
            sleep_interval = max(update_interval, min_interval)
            
            log_message("DEBUG", f"Next update check in {sleep_interval} seconds...")
            shutdown_event.wait(sleep_interval)
            
        except Exception as e:
            log_message("ERROR", f"Error in sleep interval: {e}", send_to_discord=True)
            shutdown_event.wait(60)

def optimized_handle_command_input():
    """Optimized: Handle command-line style input for the launcher"""
    config = load_config()
    poll_interval = config.get('command_poll_interval', 5)
    
    while not shutdown_event.is_set():
        try:
            if sys.stdin.isatty():
                try:
                    import msvcrt
                    # Only check for input occasionally
                    if msvcrt.kbhit():
                        char = msvcrt.getch().decode('utf-8', errors='ignore')
                        if char == '\r':
                            print("\n[COMMAND] Type 'config' to edit settings, 'help' for options: ", end='', flush=True)
                            command = ""
                            while True:
                                if msvcrt.kbhit():
                                    char = msvcrt.getch().decode('utf-8', errors='ignore')
                                    if char == '\r':
                                        print()
                                        break
                                    elif char == '\x08':
                                        if command:
                                            command = command[:-1]
                                            sys.stdout.write('\b \b')
                                            sys.stdout.flush()
                                    else:
                                        if char.isprintable():
                                            command += char
                                            sys.stdout.write(char)
                                            sys.stdout.flush()
                                else:
                                    time.sleep(0.05)  # Small sleep to reduce CPU
                            
                            process_command(command.strip().lower())
                except ImportError:
                    # Non-Windows or no msvcrt available
                    pass
                
            # Sleep to reduce CPU usage
            shutdown_event.wait(poll_interval)
                
        except Exception as e:
            log_message("ERROR", f"Command input error: {e}")
            shutdown_event.wait(5)

def process_command(command):
    """Process a single command"""
    if command == "config" or command == "editconfig":
        print("\n[COMMAND] Opening configuration editor...")
        edit_config_interactive()
    elif command == "showconfig":
        print("\n[COMMAND] Showing current configuration...")
        show_config()
    elif command == "help":
        print("\n[HELP] Available commands:")
        print("  config/editconfig - Edit configuration interactively")
        print("  showconfig        - Show current configuration")
        print("  status            - Show current status")
        print("  restart           - Restart both scripts")
        print("  restart_main      - Restart main script only")
        print("  restart_add       - Restart additional script only")
        print("  exit              - Exit the launcher")
        print("  help              - Show this help")
        print("  cpu               - Show CPU usage")
        print("  bytes             - Show current byte sizes")
        print("  verify            - Force byte verification check")
        print("  hashes            - Show current content hashes")
    elif command == "status":
        print("\n[STATUS] Launcher is running")
        print(f"  Update interval: {CONFIG.get('update_check_interval', 300)} seconds")
        print(f"  Repository: {CONFIG['repository_owner']}/{CONFIG['repository_name']}")
        print(f"  Byte verification: {'Enabled' if CONFIG.get('enable_byte_verification', True) else 'Disabled'}")
        print(f"  Cache control: {'Enabled' if CONFIG.get('enable_cache_control', True) else 'Disabled'}")
        print(f"  Cache busting: {'Enabled' if CONFIG.get('cache_busting', True) else 'Disabled'}")
        
        # Main script status
        if current_script_process:
            if current_script_process.poll() is None:
                print(f"  Main Script: Running (PID: {current_script_process.pid})")
            else:
                print(f"  Main Script: Stopped (exit code: {current_script_process.poll()})")
        else:
            print("  Main Script: Not started")
        
        # Additional script status
        if current_additional_script_process:
            if current_additional_script_process.poll() is None:
                print(f"  Additional Script: Running (PID: {current_additional_script_process.pid})")
            else:
                print(f"  Additional Script: Stopped (exit code: {current_additional_script_process.poll()})")
        elif CONFIG.get('additional_script_path'):
            print("  Additional Script: Not started (but configured)")
        else:
            print("  Additional Script: Not configured")
            
    elif command == "restart":
        print("\n[COMMAND] Restarting both scripts...")
        main_success = run_script_from_github()
        add_success = run_additional_script() if CONFIG.get('additional_script_path') else True
        if main_success and add_success:
            print("  ✓ Both scripts restarted successfully")
        else:
            print("  ✗ Failed to restart one or both scripts")
    elif command == "restart_main":
        print("\n[COMMAND] Restarting main script...")
        if run_script_from_github():
            print("  ✓ Main script restarted successfully")
        else:
            print("  ✗ Failed to restart main script")
    elif command == "restart_add":
        print("\n[COMMAND] Restarting additional script...")
        if CONFIG.get('additional_script_path'):
            if run_additional_script():
                print("  ✓ Additional script restarted successfully")
            else:
                print("  ✗ Failed to restart additional script")
        else:
            print("  ✗ No additional script configured")
    elif command == "cpu":
        cpu_info = get_cpu_usage()
        print(f"\n[CPU] Usage: {cpu_info['cpu_percent']}%")
        print(f"[CPU] Memory: {cpu_info['memory_mb']}MB")
        print(f"[CPU] Threads: {cpu_info['threads']}")
    elif command == "bytes":
        print("\n[BYTE SIZES] Current stored byte sizes:")
        for file_type in ["script", "additional", "requirements"]:
            size = get_current_byte_size(file_type)
            if size is not None:
                print(f"  {file_type:15}: {size} bytes")
            else:
                print(f"  {file_type:15}: Not stored")
    elif command == "hashes":
        print("\n[CONTENT HASHES] Current stored content hashes:")
        for file_type in ["script", "additional", "requirements"]:
            content_hash = get_current_content_hash(file_type)
            if content_hash is not None:
                print(f"  {file_type:15}: {content_hash[:16]}...")
            else:
                print(f"  {file_type:15}: Not stored")
    elif command == "verify":
        print("\n[VERIFY] Performing byte verification check...")
        config = load_config()
        for file_path, file_type in [(config['script_path'], "script"), 
                                     (config.get('additional_script_path', ''), "additional"),
                                     (config['requirements_path'], "requirements")]:
            if file_path:
                file_info = get_file_info(file_path)
                if file_info:
                    current_size = get_current_byte_size(file_type)
                    if current_size is not None:
                        if file_info['size'] != current_size:
                            print(f"  {file_type:15}: Size changed! {current_size} -> {file_info['size']} bytes")
                        else:
                            print(f"  {file_type:15}: Size unchanged ({current_size} bytes)")
                    else:
                        print(f"  {file_type:15}: No size stored (current: {file_info['size']} bytes)")
    elif command == "exit":
        print("\n[COMMAND] Exiting launcher...")
        shutdown_event.set()
    elif command:
        print(f"\n[ERROR] Unknown command: '{command}'")
        print("  Type 'help' for available commands")

def cleanup():
    """Cleanup function called on exit"""
    global shutdown_event
    shutdown_event.set()
    
    log_message("SHUTDOWN", "🛑 Launcher shutting down...", send_to_discord=True)
    
    # Stop main script
    if current_script_process and current_script_process.poll() is None:
        try:
            current_script_process.terminate()
            current_script_process.wait(timeout=5)
        except:
            pass
    
    # Stop additional script
    if current_additional_script_process and current_additional_script_process.poll() is None:
        try:
            current_additional_script_process.terminate()
            current_additional_script_process.wait(timeout=5)
        except:
            pass
    
    # Stop webhook worker
    webhook_queue.put((None, None))
    
    # Wait a moment for threads to finish
    time.sleep(2)

def main():
    """Main launcher function"""
    atexit.register(cleanup)
    
    print("=" * 60)
    print("GitHub Launcher v2.0 (Optimized CPU Version with Byte Verification)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Show CPU usage at startup
    cpu_info = get_cpu_usage()
    print(f"[CPU] Initial CPU: {cpu_info['cpu_percent']}% | Memory: {cpu_info['memory_mb']}MB")
    
    # Start webhook worker thread
    webhook_thread = threading.Thread(target=optimized_webhook_worker, daemon=True)
    webhook_thread.start()
    
    # Show configuration summary
    show_config()
    
    # Send startup notification to Discord
    config = load_config()
    startup_msg = f"🚀 GitHub Launcher v2.0 started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    log_message("STARTUP", startup_msg, send_to_discord=True)
    
    # Check if GitHub token is configured
    token = config.get('github_token')
    if not token or token == "":
        warning_msg = "No GitHub token configured - rate limits may apply"
        print("\n⚠ WARNING: " + warning_msg)
        print("  You will hit rate limits (60 requests/hour).")
        print("  Type 'config' to add your GitHub token.")
        log_message("WARNING", warning_msg, send_to_discord=True)
    else:
        print("\n✓ GitHub token configured")
    
    # Check byte verification
    if config.get('enable_byte_verification', True):
        print("✓ Byte verification enabled (will check both SHA and file size)")
        print(f"  Retries: {config.get('byte_verification_retries', 3)}")
        print(f"  Delay: {config.get('byte_verification_delay', 10)} seconds")
    else:
        print("⚠ Byte verification disabled (using SHA only)")
    
    # Check cache control
    if config.get('enable_cache_control', True):
        print("✓ Cache control enabled (bypass CDN caching)")
    else:
        print("⚠ Cache control disabled")
    
    if config.get('cache_busting', True):
        print("✓ Cache busting enabled (adds timestamp to URLs)")
    else:
        print("⚠ Cache busting disabled")
    
    # Check additional script configuration
    if config.get('additional_script_path'):
        print("✓ Additional script configured")
    else:
        print("⚠ Additional script not configured")
    
    # Check Discord logging
    if config.get('enable_discord_logging', True):
        print("✓ Discord logging enabled")
    else:
        print("⚠ Discord logging disabled")
    
    print("-" * 60)
    print("COMMANDS AVAILABLE IN CONSOLE:")
    print("  Type 'config'       - Edit configuration")
    print("  Type 'showconfig'   - Show current configuration")
    print("  Type 'status'       - Show current status")
    print("  Type 'restart'      - Restart both scripts")
    print("  Type 'restart_main' - Restart main script only")
    print("  Type 'restart_add'  - Restart additional script only")
    print("  Type 'cpu'          - Show CPU usage")
    print("  Type 'bytes'        - Show current byte sizes")
    print("  Type 'hashes'       - Show current content hashes")
    print("  Type 'verify'       - Force byte verification check")
    print("  Type 'help'         - Show command help")
    print("  Type 'exit'         - Exit the launcher")
    print("-" * 60)
    
    # Start command handler in a separate thread
    command_thread = threading.Thread(target=optimized_handle_command_input, daemon=True)
    command_thread.start()
    
    # Start update monitor
    log_message("INFO", "Starting update monitor...", send_to_discord=True)
    monitor_thread = threading.Thread(target=optimized_monitor_updates, daemon=True)
    monitor_thread.start()
    
    if initial_setup_complete:
        print("\n" + "=" * 60)
        print("✓ Launcher running")
        print(f"✓ Checking for updates every {config['update_check_interval']} seconds")
        print(f"✓ CPU monitoring every {config.get('cpu_monitor_interval', 60)} seconds")
        print(f"✓ Byte verification: {'ENABLED' if config.get('enable_byte_verification', True) else 'DISABLED'}")
        print(f"✓ Cache control: {'ENABLED' if config.get('enable_cache_control', True) else 'DISABLED'}")
        print("✓ Type 'config' in console to edit configuration")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠ Launcher starting up...")
        print("Initial setup in progress")
        print("Type 'config' in console to edit configuration")
        print("=" * 60)
    
    # Keep main thread alive with efficient waiting
    try:
        cpu_check_interval = config.get('cpu_monitor_interval', 60)
        last_cpu_display = time.time()
        
        while not shutdown_event.is_set():
            # Sleep for a while, checking periodically
            shutdown_event.wait(10)  # Check every 10 seconds
            
            # Display CPU usage periodically
            current_time = time.time()
            if current_time - last_cpu_display >= cpu_check_interval:
                cpu_info = log_cpu_usage()
                last_cpu_display = current_time
                
    except KeyboardInterrupt:
        shutdown_msg = "Launcher terminated by user"
        print(f"\n{shutdown_msg}")
        log_message("INFO", shutdown_msg, send_to_discord=True)
        shutdown_event.set()
        
    except Exception as e:
        crash_msg = f"Launcher crashed: {e}"
        log_message("CRITICAL", crash_msg, send_to_discord=True, error_details=traceback.format_exc())
        shutdown_event.set()
    
    # Wait for threads to finish
    time.sleep(2)
    sys.exit(0)

if __name__ == "__main__":
    # Check for psutil
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "--quiet"])
            import psutil
        except:
            print("Warning: Failed to install psutil. Continuing without it...")
            psutil = None
    
    main()
