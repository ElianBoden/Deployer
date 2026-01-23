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

# Global tracking of script processes
current_script_process = None
rate_limit_wait = 0
initial_setup_complete = False

def get_tracker_folder():
    """Get path to tracker folder in AppData - FIXED to use Roaming instead of Local"""
    appdata_roaming = os.getenv('APPDATA')  # Changed from LOCALAPPDATA to APPDATA
    tracker_folder = os.path.join(appdata_roaming, "GitHubLauncher")
    os.makedirs(tracker_folder, exist_ok=True)
    return tracker_folder

def get_config_path():
    """Get path to configuration file"""
    tracker_folder = get_tracker_folder()
    return os.path.join(tracker_folder, "launcher_config.json")

def load_config():
    """Load configuration from file or create default"""
    config_path = get_config_path()
    
    DEFAULT_CONFIG = {
        "update_check_interval": 300,  # Check every 5 minutes (300 seconds)
        "repository_owner": "ElianBoden",
        "repository_name": "Deployer",
        "branch": "main",
        "script_path": "script.py",
        "requirements_path": "requirements.txt",
        "github_token": "",  # Empty by default - must be set in config file
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Merge with defaults for any missing keys
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            # Save default config and return it
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    else:
        # Create config file with default values
        save_config(DEFAULT_CONFIG)
        print("Created new config file. Please edit it to add your GitHub token.")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to file"""
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # Hide the config file on Windows
        if os.name == 'nt':
            try:
                subprocess.run(['attrib', '+h', config_path], 
                             shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                pass
        
        return True
    except Exception as e:
        print(f"Failed to save config: {e}")
        return False

def log_message(level, message):
    """Log messages"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")

def check_rate_limit():
    """Check if we need to wait due to rate limiting"""
    global rate_limit_wait
    
    if rate_limit_wait > 0:
        wait_time = rate_limit_wait
        rate_limit_wait = 0
        log_message("WARNING", f"Rate limited, waiting {wait_time} seconds")
        time.sleep(wait_time)
        return True
    return False

def make_github_request(url, headers=None, retry_count=0):
    """Make a GitHub API request with rate limit handling"""
    global rate_limit_wait
    
    if retry_count >= 3:
        log_message("ERROR", f"Max retries exceeded for {url}")
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
                log_message("WARNING", f"Rate limited. Reset in {wait_time} seconds")
            else:
                rate_limit_wait = 60  # Default 60 second wait
            
            # Retry after waiting
            time.sleep(rate_limit_wait)
            return make_github_request(url, headers, retry_count + 1)
        elif e.code == 404:
            log_message("ERROR", f"File not found: {url}")
            return None
        else:
            log_message("ERROR", f"HTTP error {e.code}: {e.reason}")
            return None
    except Exception as e:
        log_message("ERROR", f"Request failed: {e}")
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
        log_message("ERROR", f"Failed to get content SHA for {file_path}: {e}")
        return None

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
                if content:  # Only return non-empty content
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
        log_message("ERROR", f"Failed to save version for {filename}: {e}")
        # Try alternative location
        try:
            alt_path = os.path.join(tempfile.gettempdir(), f"github_launcher_{filename}_version.txt")
            with open(alt_path, 'w', encoding='utf-8') as f:
                f.write(content_sha)
            log_message("INFO", f"Saved version to alternative location: {alt_path}")
            return True
        except Exception as alt_e:
            log_message("ERROR", f"Failed to save version to alternative location: {alt_e}")
            return False

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
        log_message("ERROR", f"Error checking for updates: {e}")
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
        log_message("ERROR", f"Failed to download {file_path}: {e}")
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
            log_message("ERROR", "Failed to get remote script SHA")
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
            log_message("ERROR", "Failed to download script")
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
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stderr:
                    log_message("ERROR", f"Script error: {stderr[:500]}")
            except:
                pass
            log_message("ERROR", f"Script terminated immediately: {process.returncode}")
            return False
        
        log_message("INFO", f"✓ Script started with PID: {process.pid}")
        
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
        log_message("ERROR", f"Error running script: {e}")
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
            log_message("INFO", "✓ Requirements installed successfully")
            save_current_version("requirements", remote_sha)
        else:
            stdout, stderr = process.communicate()
            if stderr:
                error_msg = stderr.decode('utf-8')[:500]
                log_message("ERROR", f"Pip error: {error_msg}")
            log_message("ERROR", f"Failed to install requirements: {process.returncode}")
        
        # Clean up
        try:
            os.remove(temp_req)
        except:
            pass
        
        return process.returncode == 0
        
    except Exception as e:
        log_message("ERROR", f"Error installing requirements: {e}")
        traceback.print_exc()
        return False

def initial_setup():
    """Perform initial setup - called once at startup"""
    global initial_setup_complete
    
    if initial_setup_complete:
        return
    
    log_message("INFO", "Performing initial setup...")
    
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
    install_requirements()
    
    # Start script
    log_message("INFO", "Starting script...")
    time.sleep(2)
    run_script_from_github()
    
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
                log_message("INFO", f"Updates detected: {', '.join(updated_files)}")
                
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
                log_message("WARNING", "Script has stopped, attempting to restart...")
                if not run_script_from_github():
                    log_message("ERROR", "Failed to restart script")
            
        except Exception as e:
            log_message("ERROR", f"Error in update monitor: {e}")
            traceback.print_exc()
        
        # Sleep for the configured interval
        try:
            config = load_config()
            interval = config.get('update_check_interval', 300)
            log_message("DEBUG", f"Next check in {interval} seconds")
            time.sleep(interval)
        except Exception as e:
            log_message("ERROR", f"Error in sleep interval: {e}")
            time.sleep(300)  # Fallback to 5 minutes

def main():
    """Main launcher function"""
    print("=" * 60)
    print("GitHub Launcher (Memory-Optimized)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Show memory-efficient info
    config = load_config()
    print(f"Repository: {config['repository_owner']}/{config['repository_name']}")
    print(f"Branch: {config['branch']}")
    print(f"Update check: every {config['update_check_interval']} seconds")
    
    # Check if GitHub token is configured
    token = config.get('github_token')
    if not token or token == "":
        print("⚠ WARNING: No GitHub token configured.")
        print("  You will hit rate limits (60 requests/hour).")
    else:
        print("✓ GitHub token configured")
        # Show first few chars of token (for verification)
        if len(token) > 12:
            print(f"  Token: {token[:8]}...{token[-4:]}")
        else:
            print(f"  Token: {token}")
    
    print("-" * 60)
    
    # Start update monitor
    log_message("INFO", "Starting update monitor...")
    monitor_thread = threading.Thread(target=monitor_updates, daemon=True)
    monitor_thread.start()
    
    if initial_setup_complete:
        print("\n" + "=" * 60)
        print("✓ Launcher running")
        print(f"✓ Checking for updates every {config['update_check_interval']} seconds")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠ Launcher starting up...")
        print("Initial setup in progress")
        print("=" * 60)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nLauncher terminated by user")
        if current_script_process and current_script_process.poll() is None:
            try:
                current_script_process.terminate()
                current_script_process.wait(timeout=5)
            except:
                pass
    
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
