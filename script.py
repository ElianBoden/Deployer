import tkinter as tk
import sys
import os

def check_and_install_tkinter():
    """Check if tkinter is available, if not, try to install it via pip"""
    try:
        import tkinter
        return True
    except ImportError:
        print("Tkinter not found. Attempting to install via pip...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
            print("Tkinter installed successfully!")
            return True
        except Exception as e:
            print(f"Failed to install tkinter: {e}")
            print("Please install it manually with: pip install tk")
            return False

def create_popup():
    """Create and display the popup window"""
    # Create the main window
    root = tk.Tk()
    root.title("Message")
    
    # Force window to stay on top
    root.attributes('-topmost', True)
    
    # Set window size and position
    window_width = 400
    window_height = 150
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    
    # Make it borderless for a more "forced" look
    root.overrideredirect(True)
    
    # Add the message
    label = tk.Label(
        root, 
        text="Je te vois adrian", 
        font=("Arial", 24, "bold"),
        fg="white",
        bg="red",
        padx=20,
        pady=20
    )
    label.pack(expand=True, fill='both')
    
    # Close after 5 seconds
    root.after(5000, root.destroy)
    
    # Run the application
    root.mainloop()

def main():
    """Main function"""
    if check_and_install_tkinter():
        create_popup()
    else:
        print("Could not create popup. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main()
