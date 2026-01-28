# additional.pyw - Debug version
import tkinter as tk
from datetime import datetime
import sys
import random

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Starting main function")
    
    # Create the main window
    window = tk.Tk()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Window created")
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Screen: {screen_width}x{screen_height}")
    
    # Calculate 50% of screen size
    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.5)
    
    # Calculate position to center the window
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set window geometry
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Window geometry set")
    
    # Remove window decorations
    window.overrideredirect(True)
    window.configure(bg='#FF0000')  # Bright red for visibility
    
    # Make window always on top
    window.attributes('-topmost', True)
    
    # Simple test effect - change color every second
    def change_color():
        colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF']
        window.configure(bg=random.choice(colors))
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Color changed")
        
        if window.winfo_exists():
            window.after(1000, change_color)
    
    # Start color changing
    change_color()
    
    # Add a label to verify window is working
    label = tk.Label(window, text="TEST WINDOW", font=("Arial", 24), fg="white", bg="black")
    label.place(relx=0.5, rely=0.5, anchor="center")
    
    # Close after 10 seconds
    def close_window():
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Closing window")
        window.destroy()
    
    window.after(10000, close_window)
    
    # Bind escape key
    window.bind('<Escape>', lambda e: window.destroy())
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Starting mainloop")
    window.mainloop()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBUG] Mainloop ended")

if __name__ == "__main__":
    main()
