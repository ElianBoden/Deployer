import tkinter as tk
import requests
import time

def create_troll_window():
    """Create a fullscreen window with images appearing and disappearing in a queue"""
    
    # Create window
    root = tk.Tk()
    root.title("")
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Set window to fullscreen
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.configure(bg='white')  # WHITE BACKGROUND
    
    # Make window stay on top
    root.attributes('-topmost', True)
    
    # Calculate cell size (10 columns x 5 rows = 50 positions)
    cell_width = screen_width // 10
    cell_height = screen_height // 5
    
    # Try to load and resize image
    img = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Use PIL to resize image to fit cell
        from io import BytesIO
        from PIL import Image, ImageTk
        
        # Open and resize image to fit cell (with some padding)
        pil_image = Image.open(BytesIO(response.content))
        pil_image = pil_image.resize((cell_width - 4, cell_height - 4), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        img = ImageTk.PhotoImage(pil_image)
        root.tk_image = img  # Keep reference
        
        print(f"Image resized to: {cell_width}x{cell_height}")
        
    except Exception as e:
        print(f"Image load failed: {e}")
        img = None
    
    # Create positions for 50 images (10 columns, 5 rows)
    positions = []
    for i in range(50):
        # Start from top-right (row 0, column 9)
        row = i // 10  # 0 to 4
        col = 9 - (i % 10)  # 9 to 0 (right to left)
        
        # Calculate position (centered in cell)
        x = col * cell_width + 2  # +2 for padding
        y = row * cell_height + 2  # +2 for padding
        
        positions.append((x, y))
    
    # Create all 50 labels initially (hidden)
    labels = []
    for i in range(50):
        if img:
            label = tk.Label(root, image=img, bg='white')
        else:
            # Fallback: simple text
            label = tk.Label(root, text="X", font=("Arial", 30), 
                           fg='black', bg='white')  # BLACK TEXT ON WHITE
        label.place(x=positions[i][0], y=positions[i][1])
        label.lower()  # Hide initially
        labels.append(label)
    
    # Counter for displayed images
    images_displayed = 0
    
    def show_next_image():
        nonlocal images_displayed
        
        if images_displayed >= 50:
            # All images have been shown
            return
        
        # Show current image
        labels[images_displayed].lift()
        
        # If we've shown 10 or more images, hide the (images_displayed - 9)th image
        # This creates the sliding window effect
        if images_displayed >= 10:
            # Hide the image that's 10 positions back
            labels[images_displayed - 10].lower()
        
        # Increment counter
        images_displayed += 1
        
        # Show next image after 0.05 seconds
        if images_displayed < 50:
            root.after(50, show_next_image)
        else:
            # After showing all, start hiding from the beginning
            root.after(1000, start_hiding)
    
    def start_hiding():
        """Start hiding images from the beginning after all are shown"""
        for i in range(50):
            root.after(i * 50, lambda idx=i: labels[idx].lower())
    
    # Start showing images after 1 second
    root.after(1000, show_next_image)
    
    # Exit on ESC
    root.bind('<Escape>', lambda e: root.destroy())
    
    # Start main loop
    root.mainloop()

# Run it
if __name__ == "__main__":
    # Check for required packages
    try:
        import requests
        from PIL import Image, ImageTk
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pillow"])
        import requests
        from PIL import Image, ImageTk
    
    create_troll_window()
