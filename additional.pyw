# additional.pyw - Test script without Unicode emojis
import time
import sys
from datetime import datetime

def main():
    print("=" * 60)
    print("ADDITIONAL SCRIPT TEST")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This script is running successfully!")
    print("The GitHub Launcher is working correctly.")
    print()
    print("You should see:")
    print("1. This output in the launcher console")
    print("2. Discord notification about script start")
    print("3. Script running in background")
    print()
    print("=" * 60)
    print("Script will run for 30 seconds to demonstrate...")
    print("=" * 60)
    
    # Keep running for 30 seconds to show it's working
    for i in range(30):
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] Script running... {30-i} seconds remaining")
        time.sleep(1)
    
    print("=" * 60)
    print("TEST COMPLETED SUCCESSFULLY")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)  # Exit with code 0 for success
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)  # Exit with code 1 for error
