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
ssl._create_default_https_context = ssl._create_unverified_context

# ============================================================================
# CONFIGURATION TABLE - Edit these values directly in the script
# ============================================================================

CONFIG = {
    # Update checking
    "update_check_interval": 10,  # Check every 5 minutes (300 seconds)
    
    # GitHub repository
    "repository_owner": "ElianBoden",
    "repository_name": "Deployer",
    "branch": "main",
    
    # File paths in repository
    "script_path": "script.py",
    "requirements_path": "requirements.txt",
    
    # GitHub token (leave empty for public repos, add token for private/higher limits)
    "github_token": "",
    
    # Discord notifications
    "enable_discord_logging": True,
    
    # Discord webhooks for error notifications
    "discord_webhooks": [
        "https://discordapp.com/api/webhooks/1464318683852832823/vF_b6uHJw7Mmo8TAvQTImzYX2Z4wzIADgPK9W3QsVBSE639CanUCr8iaer1y9_9yJqJ0",
        "https://discord.com/api/webhooks/1464319002531860563/tWigsqZ_oXEXXPa_nB0VsipH1O_SLUGel5rw-YH2iy4qg65__Gl-CVNzs5UJbaXVqzvr"
    ]
}

# ============================================================================
# END OF CONFIGURATION - DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

# Global tracking of script processes
current_script_process = None
rate_limit_wait = 0
initial_setup_complete = False

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
            # Mask token for security
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

def send_discord_notification(title, description, level="info", error_details=None):
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
        "critical": 10038562  # Dark Red
    }
    
    color = colors.get(level.lower(), colors["info"])
    
    # Prepare the embed
    embed = {
        "title": title,
        "description": description[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": []
    }
    
    # Add error details if provided
    if error_details:
        if isinstance(error_details, str):
            embed["fields"].append({
                "name": "Error Details",
                "value": error_details[:1000],
                "inline": False
            })
    
    # Add system info
    try:
        import platform
        embed["fields"].append({
            "name": "System Info",
            "value": f"OS: {platform.system()} {platform.release()}\nPython: {platform.python_version()}",
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
    
    # Send to all webhooks in a separate thread
    def send_to_webhooks():
        for webhook_url in config.get('discord_webhooks', []):
            try:
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    webhook_url,
                    data=data,
                    headers={'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req, timeout=5)
            except Exception as e:
                # Don't log Discord errors to avoid infinite loops
                pass
    
    # Start in a new thread to avoid blocking
    threading.Thread(target=send_to_webhooks, daemon=True).start()

def log_message(level, message, send_to_discord=False, error_details=None):
    """Log messages with optional Discord notification"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")
    
    # Send to Discord if requested
    if send_to_discord:
        discord_level = level.lower()
        if discord_level == "info":
            discord_level = "info"
        elif discord_level == "warning":
            discord_level = "warning"
        elif discord_level == "error":
            discord_level = "error"
        elif discord_level == "critical":
            discord_level = "critical"
        else:
            discord_level = "info"
        
        send_discord_notification(f"[{level.upper()}] {message[:100]}", message, discord_level, error_details)

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
    
    if retry_count >= 3:
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
        
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
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
                rate_limit_wait = 60  # Default 60 second wait
            
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

def get_file_content_sha(file_path):
    """Get the content SHA (blob SHA) for a file - changes when file content changes"""
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
            if 'sha' in file_info:
                return file_info['sha']
        return None
        
    except Exception as e:
        log_message("ERROR", f"Failed to get content SHA for {file_path}: {e}", send_to_discord=True)
        return None

def check_for_updates():
    """Check for updates using GitHub API with rate limit awareness"""
    config = load_config()
    updated_files = []
    
    try:
        # Get current content SHAs from GitHub
        script_content_sha = get_file_content_sha(config['script_path'])
        requirements_content_sha = get_file_content_sha(config['requirements_path'])
        
        if script_content_sha:
            current_sha = get_current_version("script")
            if current_sha:
                if script_content_sha != current_sha:
                    log_message("INFO", f"script.py content has changed (SHA: {script_content_sha[:8]})")
                    updated_files.append("script")
            else:
                # First time running, save the SHA but don't trigger update
                save_current_version("script", script_content_sha)
                log_message("INFO", f"Initial SHA saved for script.py: {script_content_sha[:8]}")
        
        if requirements_content_sha:
            current_sha = get_current_version("requirements")
            if current_sha:
                if requirements_content_sha != current_sha:
                    log_message("INFO", f"requirements.txt content has changed (SHA: {requirements_content_sha[:8]})")
                    updated_files.append("requirements")
            else:
                # First time running, save the SHA but don't trigger update
                save_current_version("requirements", requirements_content_sha)
                log_message("INFO", f"Initial SHA saved for requirements.txt: {requirements_content_sha[:8]}")
        
        return updated_files
        
    except Exception as e:
        log_message("ERROR", f"Error checking for updates: {e}", send_to_discord=True)
        return []

def download_file_direct(file_path):
    """Download file directly from raw GitHub URL"""
    config = load_config()
    
    raw_url = f"https://raw.githubusercontent.com/{config['repository_owner']}/{config['repository_name']}/{config['branch']}/{urllib.parse.quote(file_path)}"
    
    try:
        headers = {}
        # Add token for raw.githubusercontent.com if it's a private repo
        token = config.get('github_token')
        if token:
            headers['Authorization'] = f"token {token}"
        
        req = urllib.request.Request(raw_url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('utf-8')
        return content
        
    except Exception as e:
        log_message("ERROR", f"Failed to download {file_path}: {e}", send_to_discord=True)
        return None

def run_script_from_github():
    """Download and run script.py"""
    global current_script_process
    
    config = load_config()
    temp_script = None
    
    try:
        # Get current content SHA to check if we need to update
        remote_sha = get_file_content_sha(config['script_path'])
        
        if not remote_sha:
            error_msg = "Failed to get remote script SHA"
            log_message("ERROR", error_msg, send_to_discord=True)
            return False
        
        # Get current stored SHA
        current_sha = get_current_version("script")
        
        # If we already have the latest version and script is running, don't restart
        if current_sha == remote_sha and current_script_process and current_script_process.poll() is None:
            log_message("INFO", "Script is already up to date and running")
            return True
        
        # Download script
        script_content = download_file_direct(config['script_path'])
        
        if not script_content:
            error_msg = "Failed to download script"
            log_message("ERROR", error_msg, send_to_discord=True)
            return False
        
        # Save to temp file
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))
        temp_script = os.path.join(temp_dir, f"script_{timestamp}.py")
        
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        log_message("INFO", f"Script saved to: {temp_script}")
        
        # Terminate existing script process if any
        if current_script_process and current_script_process.poll() is None:
            log_message("INFO", "Terminating previous script instance")
            try:
                # Try to terminate gracefully
                current_script_process.terminate()
                try:
                    current_script_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
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
            text=True
        )
        
        current_script_process = process
        
        # Check if process starts
        time.sleep(2)
        
        if process.poll() is not None:
            # Try to read any error output
            stderr_output = ""
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stderr:
                    stderr_output = stderr[:500]
                    log_message("ERROR", f"Script error: {stderr_output}")
            except:
                pass
            
            error_msg = f"Script terminated immediately: {process.returncode}"
            log_message("ERROR", error_msg, send_to_discord=True, error_details=stderr_output)
            return False
        
        success_msg = f"✓ Script started with PID: {process.pid}"
        log_message("INFO", success_msg, send_to_discord=True)
        
        # Save content SHA after successful start
        save_current_version("script", remote_sha)
        
        # Clean up temp file after delay
        def cleanup_temp():
            time.sleep(30)
            try:
                if os.path.exists(temp_script):
                    os.remove(temp_script)
                    log_message("DEBUG", "Temp file cleaned up")
            except:
                pass
        
        threading.Thread(target=cleanup_temp, daemon=True).start()
        
        return True
        
    except Exception as e:
        error_msg = f"Error running script: {e}"
        log_message("ERROR", error_msg, send_to_discord=True, error_details=traceback.format_exc())
        traceback.print_exc()
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
        # Get current SHA to check if we need to update
        remote_sha = get_file_content_sha(config['requirements_path'])
        
        if not remote_sha:
            log_message("INFO", "No requirements.txt found or can't access")
            return True
        
        # Get current stored SHA
        current_sha = get_current_version("requirements")
        
        # Check if we need to install
        if current_sha == remote_sha:
            log_message("INFO", "Requirements already up to date")
            return True
        
        # Download requirements
        requirements_content = download_file_direct(config['requirements_path'])
        
        if not requirements_content:
            log_message("INFO", "No requirements.txt or empty")
            save_current_version("requirements", remote_sha)  # Save SHA even if empty
            return True
        
        if not requirements_content.strip():
            log_message("INFO", "Empty requirements.txt")
            save_current_version("requirements", remote_sha)  # Save SHA even if empty
            return True
        
        # Validate requirements file content
        lines = requirements_content.strip().split('\n')
        valid_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip comments and empty lines
                valid_lines.append(line)
        
        if not valid_lines:
            log_message("INFO", "No valid requirements found")
            save_current_version("requirements", remote_sha)  # Save SHA even if no valid requirements
            return True
        
        # Install requirements
        log_message("INFO", f"Installing {len(valid_lines)} requirements...")
        
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
            success_msg = "✓ Requirements installed successfully"
            log_message("INFO", success_msg, send_to_discord=True)
            save_current_version("requirements", remote_sha)
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
        traceback.print_exc()
        return False

def initial_setup():
    """Perform initial setup - called once at startup"""
    global initial_setup_complete
    
    if initial_setup_complete:
        return
    
    log_message("INFO", "Performing initial setup...", send_to_discord=True)
    
    # Get SHAs and save them without triggering updates
    config = load_config()
    
    for file_path, file_type in [(config['script_path'], "script"), 
                                 (config['requirements_path'], "requirements")]:
        content_sha = get_file_content_sha(file_path)
        if content_sha:
            current_sha = get_current_version(file_type)
            if not current_sha:
                save_current_version(file_type, content_sha)
                log_message("INFO", f"Initial SHA saved for {file_path}: {content_sha[:8]}")
    
    # Install requirements
    log_message("INFO", "Checking requirements...")
    if not install_requirements():
        log_message("WARNING", "Requirements check had issues", send_to_discord=True)
    
    # Start script
    log_message("INFO", "Starting script...")
    time.sleep(2)
    if not run_script_from_github():
        log_message("ERROR", "Failed to start script during initial setup", send_to_discord=True)
    
    initial_setup_complete = True

def monitor_updates():
    """Monitor for updates with better rate limit handling"""
    
    # Do initial setup first
    initial_setup()
    
    while True:
        try:
            config = load_config()
            interval = config.get('update_check_interval', 300)
            
            # Clear rate limit wait at the start of each check
            global rate_limit_wait
            rate_limit_wait = 0
            
            log_message("INFO", f"Checking for updates (interval: {interval}s)...")
            
            # Check for actual updates
            updated_files = check_for_updates()
            
            if updated_files:
                update_msg = f"Updates detected: {', '.join(updated_files)}"
                log_message("INFO", update_msg, send_to_discord=True)
                
                # Handle requirements first if needed
                if "requirements" in updated_files:
                    if install_requirements():
                        # Wait a bit after installing requirements
                        time.sleep(5)
                
                # Then handle script update
                if "script" in updated_files:
                    run_script_from_github()
            
            # Check if script is still running
            if current_script_process and current_script_process.poll() is not None:
                warning_msg = "Script has stopped, attempting to restart..."
                log_message("WARNING", warning_msg, send_to_discord=True)
                if not run_script_from_github():
                    error_msg = "Failed to restart script"
                    log_message("ERROR", error_msg, send_to_discord=True)
            
        except Exception as e:
            error_msg = f"Error in update monitor: {e}"
            log_message("ERROR", error_msg, send_to_discord=True, error_details=traceback.format_exc())
            traceback.print_exc()
        
        # Sleep for the configured interval
        try:
            config = load_config()
            interval = config.get('update_check_interval', 300)
            log_message("DEBUG", f"Next check in {interval} seconds")
            time.sleep(interval)
        except Exception as e:
            log_message("ERROR", f"Error in sleep interval: {e}", send_to_discord=True)
            time.sleep(300)  # Fallback to 5 minutes

def handle_command_input():
    """Handle command-line style input for the launcher"""
    while True:
        try:
            # Check if stdin is available (running in console)
            if sys.stdin.isatty():
                print("\n[COMMAND] Type 'config' to edit settings, 'help' for options: ", end='', flush=True)
                
                # Try to read input (this may fail in .pyw files)
                try:
                    import msvcrt
                    # Read characters until Enter is pressed
                    command = ""
                    while True:
                        if msvcrt.kbhit():
                            char = msvcrt.getch().decode('utf-8', errors='ignore')
                            if char == '\r':  # Enter key
                                print()  # New line
                                break
                            elif char == '\x08':  # Backspace
                                if command:
                                    command = command[:-1]
                                    sys.stdout.write('\b \b')  # Erase character
                                    sys.stdout.flush()
                            else:
                                if char.isprintable():
                                    command += char
                                    sys.stdout.write(char)
                                    sys.stdout.flush()
                    
                    command = command.strip().lower()
                    
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
                        print("  restart           - Restart the monitored script")
                        print("  exit              - Exit the launcher")
                        print("  help              - Show this help")
                    elif command == "status":
                        print("\n[STATUS] Launcher is running")
                        print(f"  Update interval: {CONFIG.get('update_check_interval', 300)} seconds")
                        print(f"  Repository: {CONFIG['repository_owner']}/{CONFIG['repository_name']}")
                        if current_script_process:
                            if current_script_process.poll() is None:
                                print(f"  Script PID: {current_script_process.pid} (running)")
                            else:
                                print(f"  Script: Not running (exit code: {current_script_process.poll()})")
                        else:
                            print("  Script: Not started")
                    elif command == "restart":
                        print("\n[COMMAND] Restarting script...")
                        if run_script_from_github():
                            print("  ✓ Script restarted successfully")
                        else:
                            print("  ✗ Failed to restart script")
                    elif command == "exit":
                        print("\n[COMMAND] Exiting launcher...")
                        if current_script_process and current_script_process.poll() is None:
                            current_script_process.terminate()
                        os._exit(0)
                    elif command:
                        print(f"\n[ERROR] Unknown command: '{command}'")
                        print("  Type 'help' for available commands")
                
                except ImportError:
                    # Not on Windows or msvcrt not available
                    time.sleep(1)
            else:
                # Not running in interactive terminal, just sleep
                time.sleep(5)
                
        except Exception as e:
            # If there's any error, just sleep and continue
            time.sleep(5)

def main():
    """Main launcher function"""
    print("=" * 60)
    print("GitHub Launcher (Memory-Optimized)")
    print(f"Started: {datetime.now().strftime('%Y-%m-d %H:%M:%S')}")
    print("=" * 60)
    
    # Show configuration summary
    show_config()
    
    # Send startup notification to Discord
    config = load_config()
    startup_msg = f"GitHub Launcher started on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    log_message("INFO", startup_msg, send_to_discord=True)
    
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
    print("  Type 'restart'      - Restart the monitored script")
    print("  Type 'help'         - Show command help")
    print("  Type 'exit'         - Exit the launcher")
    print("-" * 60)
    
    # Start command handler in a separate thread
    command_thread = threading.Thread(target=handle_command_input, daemon=True)
    command_thread.start()
    
    # Start update monitor
    log_message("INFO", "Starting update monitor...")
    monitor_thread = threading.Thread(target=monitor_updates, daemon=True)
    monitor_thread.start()
    
    if initial_setup_complete:
        print("\n" + "=" * 60)
        print("✓ Launcher running")
        print(f"✓ Checking for updates every {config['update_check_interval']} seconds")
        print("✓ Type 'config' in console to edit configuration")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠ Launcher starting up...")
        print("Initial setup in progress")
        print("Type 'config' in console to edit configuration")
        print("=" * 60)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        shutdown_msg = "Launcher terminated by user"
        print(f"\n{shutdown_msg}")
        log_message("INFO", shutdown_msg, send_to_discord=True)
        if current_script_process and current_script_process.poll() is None:
            try:
                current_script_process.terminate()
                current_script_process.wait(timeout=5)
            except:
                pass
    except Exception as e:
        crash_msg = f"Launcher crashed: {e}"
        log_message("CRITICAL", crash_msg, send_to_discord=True, error_details=traceback.format_exc())
        raise
    
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
