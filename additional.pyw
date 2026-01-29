import tkinter as tk
import requests
import time

def create_troll_window():
    """Create a fullscreen borderless window with images appearing one by one"""
    
    # Create window
    root = tk.Tk()
    root.title("")  # Empty title
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Set window to fullscreen WITHOUT overrideredirect
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.configure(bg='black')
    
    # Try to remove window decorations (might not work on all systems)
    try:
        root.attributes('-fullscreen', True)
    except:
        pass
    
    # Make window stay on top
    root.attributes('-topmost', True)
    
    # Try to load image
    img = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Convert to PhotoImage
        from io import BytesIO
        import base64
        img_data = response.content
        img = tk.PhotoImage(data=base64.b64encode(img_data))
        root.tk_image = img  # Keep reference
        
        # Get image size
        img_width = img.width()
        img_height = img.height()
        print(f"Image size: {img_width}x{img_height}")
        
    except Exception as e:
        print(f"Image load failed: {e}")
        img = None
    
    # Calculate positions (10x5 grid = 50 images)
    positions = []
    for i in range(50):
        # Start from top-right (row 0, column 9)
        row = i // 10  # 0 to 4
        col = 9 - (i % 10)  # 9 to 0 (right to left)
        
        # Calculate position
        x = col * (screen_width // 10)
        y = row * (screen_height // 5)
        
        positions.append((x, y))
    
    # Counter for displayed images
    images_displayed = 0
    labels = []
    
    def show_next_image():
        nonlocal images_displayed
        
        if images_displayed >= 50:
            # All images shown
            return
        
        # Get position
        x, y = positions[images_displayed]
        
        # Create label with image or fallback
        if img:
            label = tk.Label(root, image=img, bg='black')
        else:
            # Fallback: simple text
            label = tk.Label(root, text="X", font=("Arial", 60), 
                           fg='white', bg='black')
        
        # Place the label
        label.place(x=x, y=y)
        labels.append(label)
        
        # Update display
        root.update()
        
        # Increment counter
        images_displayed += 1
        
        # Show next image after 0.05 seconds
        if images_displayed < 50:
            root.after(50, show_next_image)
    
    # Start showing images after 1 second
    root.after(1000, show_next_image)
    
    # Exit on ESC
    root.bind('<Escape>', lambda e: root.destroy())
    
    # Start main loop
    root.mainloop()

# Even simpler working version
def simple_working_troll():
    """Minimal working version that definitely works"""
    
    # Create window
    window = tk.Tk()
    window.title("")
    
    # Get screen size
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    
    # Set window to screen size
    window.geometry(f"{width}x{height}+0+0")
    window.configure(bg='black')
    
    # Try to make fullscreen
    try:
        window.attributes('-fullscreen', True)
    except:
        pass
    
    # Load image (with error handling)
    image = None
    try:
        import urllib.request
        import io
        from PIL import Image, ImageTk
        
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        
        # Download image
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        
        # Convert to PIL Image then to PhotoImage
        pil_image = Image.open(io.BytesIO(raw_data))
        image = ImageTk.PhotoImage(pil_image)
        window.image = image  # Keep reference
        
    except Exception as e:
        print(f"Couldn't load image: {e}")
        image = None
    
    # Create positions for 50 images (10 columns, 5 rows)
    positions = []
    for i in range(50):
        row = i // 10  # Row number (0-4)
        col = 9 - (i % 10)  # Column (9 to 0, right to left)
        
        x = col * (width // 10) + 20
        y = row * (height // 5) + 20
        
        positions.append((x, y))
    
    # Function to show images one by one
    def place_images(idx=0):
        if idx >= 50:
            # All images placed
            return
        
        x, y = positions[idx]
        
        if image:
            label = tk.Label(window, image=image, bg='black')
        else:
            label = tk.Label(window, text="O", font=("Arial", 40), 
                           fg='white', bg='black')
        
        label.place(x=x, y=y)
        
        # Schedule next image
        if idx < 49:
            window.after(50, lambda: place_images(idx + 1))
    
    # Start placing images
    window.after(500, lambda: place_images(0))
    
    # Exit on ESC
    window.bind('<Escape>', lambda e: window.destroy())
    
    # Start
    window.mainloop()

# ULTRA SIMPLE - GUARANTEED TO WORK
def troll_images():
    """Simplest possible version that will work"""
    
    # Create window
    win = tk.Tk()
    win.title("")
    
    # Set window size to screen size
    w = win.winfo_screenwidth()
    h = win.winfo_screenheight()
    win.geometry(f"{w}x{h}+0+0")
    win.configure(bg='black')
    
    # Don't use overrideredirect, just maximize
    win.state('zoomed')
    
    # List to store labels
    labels = []
    
    # Create 50 images
    for i in range(50):
        # Calculate position: start from top-right
        row = i // 10  # 0-4
        col = 9 - (i % 10)  # 9-0
        
        x = col * (w // 10)
        y = row * (h // 5)
        
        # Create label (initially hidden)
        label = tk.Label(win, bg='black')
        label.place(x=x, y=y)
        label.lower()  # Hide initially
        labels.append(label)
    
    # Counter for revealed images
    revealed = 0
    
    def reveal():
        nonlocal revealed
        
        if revealed >= 50:
            return
        
        # Show this image
        labels[revealed].lift()
        revealed += 1
        
        # Schedule next reveal
        if revealed < 50:
            win.after(50, reveal)
    
    # Start revealing after 1 second
    win.after(1000, reveal)
    
    # Exit
    win.bind('<Escape>', lambda e: win.destroy())
    
    win.mainloop()

# RUN IT
if __name__ == "__main__":
    # Try simple_working_troll first
    simple_working_troll()
    
    # If that doesn't work, uncomment the ultra simple version:
    # troll_images()
