# monitor_script.py - Kills old launcher and cleans up files only
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
:: (Be careful not to kill this monitor script)
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
    """Clean up old files from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    print("Cleaning up files from startup folder...")
    
    # List of files to delete (only old/obsolete ones)
    files_to_delete = [
        "startup_log.txt",
        "github_launcher.pyw",
        "update_cache.json",
        "requirements.txt",
        "clean_launcher.pyw",
        "old_launcher_backup.pyw",
        "launcher_update.py"
    ]
    
    deleted = []
    failed = []
    
    for filename in files_to_delete:
        filepath = os.path.join(startup_folder, filename)
        if os.path.exists(filepath):
            try:
                # Try to delete the file
                for attempt in range(3):
                    try:
                        os.remove(filepath)
                        deleted.append(filename)
                        print(f"  ✓ Deleted: {filename}")
                        break
                    except PermissionError:
                        if attempt < 2:
                            time.sleep(1)
                        else:
                            failed.append(filename)
                    except Exception as e:
                        failed.append(filename)
            except:
                failed.append(filename)
    
    # Also clean up any temporary monitor scripts
    temp_dir = tempfile.gettempdir()
    for file in os.listdir(temp_dir):
        if file.startswith("monitor_") and file.endswith(".py"):
            try:
                filepath = os.path.join(temp_dir, file)
                os.remove(filepath)
                print(f"  ✓ Deleted temp file: {file}")
            except:
                pass
    
    # Summary
    if deleted:
        print(f"\nSuccessfully deleted: {', '.join(deleted)}")
    if failed:
        print(f"Failed to delete: {', '.join(failed)}")
    
    return len(deleted) > 0

def delete_self():
    """Delete this monitor script after completion"""
    try:
        # Wait a moment to ensure everything is done
        time.sleep(2)
        
        # Get current script path
        script_path = os.path.abspath(__file__)
        
        # Only delete if in temp directory
        if 'temp' in script_path.lower() or 'tmp' in script_path.lower():
            # Create batch file to delete this script
            batch_script = f'''@echo off
timeout /t 2 /nobreak >nul
del "{script_path}" 2>nul
echo Monitor script cleaned up
del "%~f0" 2>nul
'''
            
            batch_path = os.path.join(tempfile.gettempdir(), "delete_self.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_script)
            
            subprocess.Popen(['cmd', '/c', batch_path],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            print("Self-cleanup scheduled")
    except:
        pass

def main():
    """Main cleanup function - only does cleanup, no launcher creation"""
    print("=" * 60)
    print("LAUNCHER CLEANUP TOOL")
    print("=" * 60)
    
    # Step 1: Kill old launcher processes
    print("\n[1/2] Killing old launcher processes...")
    kill_old_launcher()
    print("✓ Old launcher processes terminated")
    
    # Step 2: Clean up files
    print("\n[2/2] Cleaning up old files...")
    cleanup_success = cleanup_files()
    
    # Send webhook notification
    if cleanup_success:
        send_webhook("🧹 Launcher cleanup completed! Old processes killed and files removed.")
        print("\n✓ Cleanup completed successfully")
    else:
        send_webhook("⚠️ Launcher cleanup attempted but some files may remain")
        print("\n⚠️ Cleanup completed with some issues")
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)
    
    # Schedule self-deletion if running from temp
    delete_self()
    
    # Exit
    time.sleep(2)
    sys.exit(0 if cleanup_success else 1)

if __name__ == "__main__":
    main()
