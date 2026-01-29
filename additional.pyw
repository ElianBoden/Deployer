import tkinter as tk
import requests
import time
import threading

def create_sliding_troll_window():
    """Create a borderless fullscreen window with sliding image effect"""
    
    # Create window with NO TITLE BAR
    root = tk.Tk()
    root.title("")  # Empty title
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Remove window decorations for NO TAB
    root.overrideredirect(True)
    
    # Set window to cover entire screen
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.configure(bg='white')
    
    # Make window stay on top
    root.attributes('-topmost', True)
    
    print(f"Screen: {screen_width}x{screen_height}")
    print("Starting sliding image display...")
    print("Window has NO tabs/borders - fullscreen")
    print("-" * 50)
    
    # Calculate cell size (10 columns x 5 rows = 50 positions)
    cell_width = screen_width // 10
    cell_height = screen_height // 5
    
    # Try to load and resize image
    img = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Use PIL to resize image
        from io import BytesIO
        from PIL import Image, ImageTk
        
        # Open and resize image to fit cell
        pil_image = Image.open(BytesIO(response.content))
        pil_image = pil_image.resize((cell_width - 4, cell_height - 4), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        img = ImageTk.PhotoImage(pil_image)
        root.tk_image = img  # Keep reference
        
        print(f"Image resized to: {cell_width - 4}x{cell_height - 4}")
        
    except Exception as e:
        print(f"Image load failed: {e}")
        img = None
    
    # Queue to track the last 10 images
    image_queue = []
    
    # Counter for total images created
    total_images_created = 0
    
    # Current position index (0-49)
    current_position = 0
    
    def calculate_position(index):
        """Calculate screen position for image at given index (0-49)"""
        # Start from top-right (index 0 = top-right corner)
        row = index // 10  # 0 to 4
        col = 9 - (index % 10)  # 9 to 0 (right to left)
        
        # Calculate pixel position (centered in cell)
        x = col * cell_width + 2
        y = row * cell_height + 2
        
        return (x, y)
    
    def create_and_show_image():
        """Create a new image, show it, and manage the queue"""
        nonlocal total_images_created, current_position
        
        if total_images_created >= 50:
            return  # Done showing all images
        
        # Calculate position for this image
        x, y = calculate_position(current_position)
        
        # Create the image label
        if img:
            label = tk.Label(root, image=img, bg='white')
        else:
            # Fallback: number label
            label = tk.Label(root, text=str(total_images_created + 1), 
                           font=("Arial", 20), fg='black', bg='white',
                           bd=1, relief='solid')
        
        # Place the image
        label.place(x=x, y=y)
        
        # Add to queue
        image_queue.append(label)
        
        # Print progress
        print(f"Image {total_images_created + 1}/50 created at position {current_position + 1}")
        
        # Update counters
        total_images_created += 1
        current_position += 1
        
        # If queue has more than 10, remove the oldest
        if len(image_queue) > 10:
            # Remove the oldest image
            oldest_label = image_queue.pop(0)
            oldest_label.destroy()
            print(f"  Removed oldest image (queue size: {len(image_queue)})")
        
        # Schedule next image if not done
        if total_images_created < 50:
            root.after(50, create_and_show_image)
        else:
            print("\nAll 50 images have been created!")
            print(f"Final queue size: {len(image_queue)} images visible")
    
    # Start showing images after 1 second
    root.after(1000, create_and_show_image)
    
    # Exit on ESC (but window has no title bar, so need alternative)
    root.bind('<Escape>', lambda e: root.destroy())
    
    # Also exit on Alt+F4 (Windows) or Ctrl+W (some systems)
    root.bind('<Alt-F4>', lambda e: root.destroy())
    
    # Add a hidden close button in corner (transparent)
    close_btn = tk.Label(root, text="X", font=("Arial", 12), 
                        fg='#CCCCCC', bg='white', cursor='hand2')
    close_btn.place(x=screen_width-30, y=5)
    close_btn.bind('<Button-1>', lambda e: root.destroy())
    
    print("\nInstructions:")
    print("- Images will appear one by one every 0.05 seconds")
    print("- After 10 images, oldest will be destroyed as new ones appear")
    print("- Press ESC or click the faint 'X' in top-right to exit")
    print("-" * 50)
    
    # Start main loop
    root.mainloop()

# Alternative version with visual feedback
def sliding_troll_visual():
    """Version with better visual feedback"""
    
    # Create window
    root = tk.Tk()
    root.title("")
    root.overrideredirect(True)  # NO TABS
    
    # Screen size
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+0+0")
    root.configure(bg='white')
    
    # Cell size
    cell_w = w // 10
    cell_h = h // 5
    
    # Load image
    photo = None
    try:
        import urllib.request
        import io
        from PIL import Image, ImageTk
        
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        with urllib.request.urlopen(url) as response:
            img_data = response.read()
        
        pil_img = Image.open(io.BytesIO(img_data))
        pil_img = pil_img.resize((cell_w - 10, cell_h - 10), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(pil_img)
        root.photo = photo
        
    except:
        photo = None
    
    # Create ALL positions in advance
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)
        x = col * cell_w + 5
        y = row * cell_h + 5
        positions.append((x, y))
    
    # Queue system
    queue = []
    current_idx = 0
    
    def add_image():
        nonlocal current_idx
        
        if current_idx >= 50:
            return
        
        # Create new image
        if photo:
            lbl = tk.Label(root, image=photo, bg='white')
        else:
            lbl = tk.Label(root, text=str(current_idx + 1), 
                          font=("Arial", 16), fg='black', bg='white')
        
        x, y = positions[current_idx]
        lbl.place(x=x, y=y)
        
        # Add to queue
        queue.append(lbl)
        
        # Remove oldest if queue > 10
        if len(queue) > 10:
            old = queue.pop(0)
            old.destroy()
        
        current_idx += 1
        
        # Schedule next
        if current_idx < 50:
            root.after(50, add_image)
    
    # Start
    root.after(500, add_image)
    
    # Exit
    root.bind('<Escape>', lambda e: root.destroy())
    
    # Add status text (fades out)
    status = tk.Label(root, text="Images: 0/50   Queue: 0", 
                     font=("Arial", 10), fg='gray', bg='white')
    status.place(x=10, y=10)
    
    def update_status():
        if current_idx < 50:
            status.config(text=f"Images: {current_idx}/50   Queue: {len(queue)}")
            root.after(100, update_status)
    
    root.after(600, update_status)
    
    root.mainloop()

# Run the simplest version
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
    
    # Run the main function
    create_sliding_troll_window()
