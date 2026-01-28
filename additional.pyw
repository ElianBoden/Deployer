# additional.pyw - Test script that shows a window for 5 seconds (Windows compatible)
import tkinter as tk
import time
import sys
from datetime import datetime

def main():
    # Create the main window
    window = tk.Tk()
    window.title("GitHub Launcher Test")
    window.geometry("400x250")
    window.configure(bg='#2b2b2b')
    
    # Center the window on screen
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Add title label
    title_label = tk.Label(
        window, 
        text="Test Window - Additional Script", 
        font=("Arial", 16, "bold"),
        fg="white",
        bg="#2b2b2b"
    )
    title_label.pack(pady=20)
    
    # Add status label
    status_label = tk.Label(
        window,
        text="This window will close in:",
        font=("Arial", 12),
        fg="white",
        bg="#2b2b2b"
    )
    status_label.pack(pady=10)
    
    # Add countdown label
    countdown_label = tk.Label(
        window,
        text="5 seconds",
        font=("Arial", 24, "bold"),
        fg="#00ff00",
        bg="#2b2b2b"
    )
    countdown_label.pack(pady=10)
    
    # Add info text
    info_label = tk.Label(
        window,
        text="Check Discord for success notification!",
        font=("Arial", 10),
        fg="#cccccc",
        bg="#2b2b2b"
    )
    info_label.pack(pady=10)
    
    # Function to update countdown
    def update_countdown(seconds_left):
        if seconds_left > 0:
            countdown_label.config(text=f"{seconds_left} second{'s' if seconds_left > 1 else ''}")
            window.after(1000, update_countdown, seconds_left - 1)
        else:
            window.destroy()
    
    # Start countdown
    update_countdown(5)
    
    # Print to console - using only ASCII characters to avoid encoding issues
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [SUCCESS] Test window created!")
    print(f"[{current_time}] [INFO] Window will close in 5 seconds")
    print(f"[{current_time}] [INFO] This confirms additional script is working!")
    print(f"[{current_time}] [INFO] Check Discord for notification")
    
    # Run the main loop
    window.mainloop()
    
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] Test window closed successfully!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"[{current_time}] [ERROR] {e}")
        sys.exit(1)
