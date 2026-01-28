# additional.pyw - Display an image in a window that takes 50% of screen
import tkinter as tk
from tkinter import ttk
import urllib.request
import io
from datetime import datetime
import sys
import time

def main():
    # Create the main window
    window = tk.Tk()
    window.title("GitHub Launcher - Image Test")
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate 50% of screen size (centered)
    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.5)
    
    # Calculate position to center the window
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set window geometry
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Remove window decorations for cleaner look
    window.overrideredirect(False)  # Set to True if you want no title bar
    window.configure(bg='black')
    
    # Add a label
    label = tk.Label(
        window,
        text="GitHub Launcher Test - Displaying Image",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="black"
    )
    label.pack(pady=10)
    
    # Add countdown label
    countdown_var = tk.StringVar()
    countdown_var.set("Window will close in: 5 seconds")
    
    countdown_label = tk.Label(
        window,
        textvariable=countdown_var,
        font=("Arial", 12),
        fg="#00ff00",
        bg="black"
    )
    countdown_label.pack(pady=5)
    
    # Create a frame for the image
    image_frame = tk.Frame(window, bg="black")
    image_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)
    
    # Try to load and display the image
    try:
        # Image URL (using the 870w version for faster loading)
        image_url = "https://images.unsplash.com/photo-1562860149-691401a306f8?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        
        # Download image
        with urllib.request.urlopen(image_url) as response:
            image_data = response.read()
        
        # Convert to PhotoImage
        from PIL import Image, ImageTk
        import io
        
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Resize image to fit the frame (leaving some padding)
        frame_width = window_width - 40
        frame_height = window_height - 100
        
        # Calculate aspect ratio
        img_ratio = image.width / image.height
        frame_ratio = frame_width / frame_height
        
        if img_ratio > frame_ratio:
            # Image is wider than frame
            new_width = frame_width
            new_height = int(frame_width / img_ratio)
        else:
            # Image is taller than frame
            new_height = frame_height
            new_width = int(frame_height * img_ratio)
        
        # Resize image
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Create label to display image
        image_label = tk.Label(image_frame, image=photo, bg="black")
        image_label.image = photo  # Keep a reference to avoid garbage collection
        image_label.pack(expand=True)
        
        # Add caption
        caption_label = tk.Label(
            window,
            text="City Skyline at Night - GitHub Launcher Test",
            font=("Arial", 10),
            fg="white",
            bg="black"
        )
        caption_label.pack(pady=5)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Image loaded and displayed successfully")
        
    except Exception as e:
        # If image loading fails, show an error message
        error_label = tk.Label(
            image_frame,
            text=f"Failed to load image: {str(e)[:100]}",
            font=("Arial", 12),
            fg="red",
            bg="black",
            wraplength=window_width - 100
        )
        error_label.pack(expand=True)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Failed to load image: {e}")
    
    # Function to update countdown
    def update_countdown(seconds_left):
        if seconds_left > 0:
            countdown_var.set(f"Window will close in: {seconds_left} second{'s' if seconds_left > 1 else ''}")
            window.after(1000, update_countdown, seconds_left - 1)
        else:
            window.destroy()
    
    # Start countdown
    update_countdown(5)
    
    # Print to console
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] Window created - 50% of screen")
    print(f"[{current_time}] [INFO] Screen size: {screen_width}x{screen_height}")
    print(f"[{current_time}] [INFO] Window size: {window_width}x{window_height}")
    print(f"[{current_time}] [INFO] Window will close in 5 seconds")
    
    # Run the window
    window.mainloop()
    
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [SUCCESS] Window closed successfully!")

if __name__ == "__main__":
    try:
        # Try to import required modules
        try:
            from PIL import Image, ImageTk
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Installing Pillow...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--quiet"])
            from PIL import Image, ImageTk
        
        main()
        sys.exit(0)  # Exit with code 0 for success
    except KeyboardInterrupt:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {e}")
        sys.exit(1)
