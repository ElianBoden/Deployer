import os
import sys
import json
import urllib.request
import subprocess
import time
import traceback
import psutil
from pathlib import Path

def update_discord_state(state):
    """Update Discord Rich Presence state"""
    try:
        # This will be called by the main script, so just log for now
        print(f"Discord state: {state}")
        
        # If there's an existing Discord RPC connection, you could update it here
        # For now, we'll just print the state
        
        # Example if you have Discord RPC:
        # if discord_rpc_initialized:
        #     discord_rpc.update_presence(state=state)
        
        return True
    except Exception as e:
        print(f"Failed to update Discord state: {e}")
        return False

def read_config():
    """Read the config.json file"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        print("config.json not found, using defaults")
        return {"update-launcher": False}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error reading config.json: {e}")
        return {"update-launcher": False}

def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        response = urllib.request.urlopen(url, timeout=10)
        content = response.read()
        
        with open(destination, 'wb') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def kill_python_processes(exclude_pid=None):
    """Kill all Python processes except the specified PID"""
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if it's a Python process
            if ('python' in proc.info['name'].lower() or 
                'pythonw' in proc.info['name'].lower() or
                proc.info['name'].lower().endswith('.py') or
                proc.info['name'].lower().endswith('.pyw')):
                
                pid = proc.info['pid']
                
                # Don't kill the new process or current process
                if pid != exclude_pid and pid != current_pid:
                    try:
                        proc.kill()
                        print(f"Killed Python process PID: {pid}")
                        time.sleep(0.1)
                    except:
                        pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def perform_update():
    """Perform the launcher update"""
    print("Performing launcher update...")
    
    # Update Discord state
    update_discord_state("Updating launcher...")
    
    # Delete old launcher files
    launcher_files = ["Startup.pyw", "github_launcher.pyw"]
    for launcher_file in launcher_files:
        if os.path.exists(launcher_file):
            try:
                os.remove(launcher_file)
                print(f"Deleted: {launcher_file}")
            except Exception as e:
                print(f"Error deleting {launcher_file}: {e}")
    
    # Download the new launcher
    new_launcher_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
    new_launcher_path = "Startup.pyw"
    
    if download_file(new_launcher_url, new_launcher_path):
        print("Downloaded new launcher successfully")
        
        # Start the new launcher
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            new_process = subprocess.Popen(
                [sys.executable, new_launcher_path],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            print(f"Started new launcher with PID: {new_process.pid}")
            
            # Update Discord state
            update_discord_state("Launcher updated, starting...")
            
            # Kill all other Python processes (including this one)
            time.sleep(2)  # Give new process time to start
            kill_python_processes(new_process.pid)
            
            # Exit this process
            sys.exit(0)
            
        except Exception as e:
            print(f"Error starting new launcher: {e}")
            return False
    else:
        print("Failed to download new launcher")
        return False

def run_launcher():
    """Run the appropriate launcher"""
    # Check which launcher exists
    if os.path.exists("github_launcher.pyw"):
        launcher = "github_launcher.pyw"
    elif os.path.exists("Startup.pyw"):
        launcher = "Startup.pyw"
    else:
        print("No launcher found, downloading default...")
        if not download_file("https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw", "github_launcher.pyw"):
            print("Failed to download launcher")
            return False
        launcher = "github_launcher.pyw"
    
    # Update Discord state
    update_discord_state("Starting launcher...")
    
    # Run the launcher
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, launcher],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"Started {launcher} with PID: {process.pid}")
        return True
        
    except Exception as e:
        print(f"Error starting launcher: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Launcher Update Checker")
    print("=" * 60)
    
    # Update Discord state
    update_discord_state("Checking for updates...")
    
    # Read config
    config = read_config()
    
    # Check if update is requested
    if config.get("update-launcher", False):
        print("Update requested in config.json")
        
        # Perform the update
        success = perform_update()
        
        if not success:
            print("Update failed, running existing launcher...")
            run_launcher()
    else:
        print("No update requested, running existing launcher...")
        run_launcher()
    
    # Wait a bit before exiting
    time.sleep(3)
    print("Update checker completed")

if __name__ == "__main__":
    # Make sure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    main()
