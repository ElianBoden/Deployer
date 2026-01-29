import tkinter as tk
from tkinter import PhotoImage
import requests
from io import BytesIO
import time
import threading

def create_troll_window():
    """Create a window that displays images in a trolling pattern"""
    
    # Create the main window
    root = tk.Tk()
    root.title("Troll Images")
    
    # Remove window decorations for maximum troll effect
    root.overrideredirect(True)  # No title bar
    
    # Make window fullscreen
    root.attributes('-fullscreen', True)
    root.configure(bg='white')
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Download the image
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        img_data = BytesIO(response.content)
        
        # Convert to PhotoImage for tkinter
        photo = PhotoImage(data=img_data.read())
        
        # Store reference to prevent garbage collection
        root.tk_image = photo
        
        # Get image dimensions
        img_width = photo.width()
        img_height = photo.height()
        
        print(f"Image loaded: {img_width}x{img_height}")
        print(f"Screen size: {screen_width}x{screen_height}")
        
    except Exception as e:
        print(f"Error loading image: {e}")
        # Use a default smiley face if image fails
        photo = None
        img_width = 100
        img_height = 100
    
    # Grid layout: 10 columns x 5 rows = 50 images
    cols = 10
    rows = 5
    
    # Calculate spacing
    col_spacing = screen_width // cols
    row_spacing = screen_height // rows
    
    # List to hold image labels
    image_labels = []
    
    def place_image(index):
        """Place one image at its position with delay"""
        if index >= 50:
            return
            
        # Calculate position (starting from top-right)
        row = index // cols  # 0 to 4
        col_in_row = index % cols  # 0 to 9
        col = cols - 1 - col_in_row  # Start from rightmost column (9 to 0)
        
        # Calculate coordinates (centered in cell)
        x = col * col_spacing + (col_spacing - img_width) // 2
        y = row * row_spacing + (row_spacing - img_height) // 2
        
        if photo:
            # Create label with image
            label = tk.Label(root, image=photo, bg='white')
        else:
            # Fallback to text if image failed
            label = tk.Label(root, text="😂", font=("Arial", 40), bg='white')
        
        label.place(x=x, y=y)
        image_labels.append(label)
        
        print(f"Placed image {index + 1}/50 at position ({row+1},{col+1})")
        
        # Schedule next image
        if index < 49:
            root.after(50, lambda: place_image(index + 1))
    
    # Start placing images after a short delay
    root.after(100, lambda: place_image(0))
    
    # Add exit instructions (hidden at first)
    exit_label = tk.Label(root, text="Press ESC to exit", 
                         font=("Arial", 16), bg='white', fg='red')
    exit_label.place(relx=0.5, rely=0.5, anchor='center')
    exit_label.lower()  # Send to back
    
    def show_exit():
        """Show exit instructions"""
        exit_label.lift()
        exit_label.after(2000, exit_label.lower)
    
    # Bind escape key to close
    def close_window(event=None):
        root.destroy()
    
    root.bind('<Escape>', close_window)
    root.bind('<Control-c>', close_window)
    root.bind('<Control-q>', close_window)
    root.bind('<Button-1>', lambda e: show_exit())  # Click to show exit hint
    
    # Make window stay on top
    root.attributes('-topmost', True)
    
    print("=" * 60)
    print("TROLL IMAGE DISPLAY ACTIVATED")
    print("Images will appear one by one from top-right corner")
    print("Press ESC to exit the troll window")
    print("=" * 60)
    
    # Start the main loop
    root.mainloop()

def quick_troll():
    """Simpler troll version"""
    import tkinter as tk
    from tkinter import PhotoImage
    import requests
    from io import BytesIO
    
    # Create window
    root = tk.Tk()
    root.title("😂 TROLL TIME 😂")
    root.attributes('-fullscreen', True)
    root.configure(bg='white')
    
    # Download image
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url)
        photo = PhotoImage(data=BytesIO(response.content).read())
        root.tk_image = photo  # Keep reference
    except:
        photo = None
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Create all labels but hide them initially
    labels = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)  # Start from right
        
        x = (col * screen_width // 10) + 20
        y = (row * screen_height // 5) + 20
        
        if photo:
            label = tk.Label(root, image=photo, bg='white')
        else:
            label = tk.Label(root, text="💀", font=("Arial", 30), bg='white')
        
        label.place(x=x, y=y)
        label.lower()  # Hide initially
        labels.append(label)
    
    # Function to reveal images one by one
    def reveal_image(idx=0):
        if idx < len(labels):
            labels[idx].lift()  # Show this image
            root.after(50, lambda: reveal_image(idx + 1))  # Next in 0.05s
    
    # Start revealing
    root.after(100, lambda: reveal_image(0))
    
    # Exit on ESC
    root.bind('<Escape>', lambda e: root.destroy())
    
    # Click anywhere to show/hide exit hint
    exit_hint = tk.Label(root, text="ESC to exit", font=("Arial", 20), 
                        bg='red', fg='white')
    exit_hint.place(relx=0.5, rely=0.95, anchor='center')
    exit_hint.lower()
    
    def toggle_hint():
        if exit_hint.winfo_viewable():
            exit_hint.lower()
        else:
            exit_hint.lift()
    
    root.bind('<Button-1>', lambda e: toggle_hint())
    
    print("TROLL WINDOW ACTIVATED - Images appearing one by one!")
    print("Starting from top-right corner...")
    
    root.mainloop()

if __name__ == "__main__":
    # Try to install requests if needed
    try:
        import requests
    except:
        import os
        os.system("pip install requests")
        import requests
    
    # Run the troll window
    quick_troll()
