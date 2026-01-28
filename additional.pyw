# additional.pyw - Test script that shows a window for 5 seconds
import tkinter as tk
import time
from datetime import datetime

def main():
    # Create the main window
    window = tk.Tk()
    window.title("GitHub Launcher Test")
    window.geometry("400x300")
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
        text="✅ Additional Script Test", 
        font=("Arial", 18, "bold"),
        fg="white",
        bg="#2b2b2b"
    )
    title_label.pack(pady=30)
    
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
    countdown_label.pack(pady=20)
    
    # Add info text
    info_text = tk.Text(
        window,
        height=5,
        width=40,
        bg="#3c3c3c",
        fg="white",
        font=("Arial", 10),
        relief="flat",
        borderwidth=0
    )
    info_text.pack(pady=10)
    info_text.insert("1.0", "• Script started successfully!\n• Window will auto-close in 5 seconds\n• This confirms the launcher is working\n• Check Discord for notifications")
    info_text.configure(state="disabled")
    
    # Add close button
    close_button = tk.Button(
        window,
        text="Close Now",
        command=window.destroy,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 12),
        relief="raised",
        borderwidth=2
    )
    close_button.pack(pady=10)
    
    # Function to update countdown
    def update_countdown(seconds_left):
        if seconds_left > 0:
            countdown_label.config(text=f"{seconds_left} second{'s' if seconds_left > 1 else ''}")
            window.after(1000, update_countdown, seconds_left - 1)
        else:
            window.destroy()
    
    # Start countdown
    update_countdown(5)
    
    # Print to console (will be captured by launcher)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Test window created!")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🪟 Window will close in 5 seconds")
    
    # Run the main loop
    window.mainloop()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 👋 Test window closed successfully!")

if __name__ == "__main__":
    main()
