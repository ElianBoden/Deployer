import tkinter as tk
import requests
import time
from io import BytesIO
from PIL import Image, ImageTk

def create_real_image_troll():
    """Display actual images from URL with transparent background"""
    
    # Create main window
    root = tk.Tk()
    root.title("")
    
    # Remove all window decorations
    root.overrideredirect(True)
    
    # Get screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Set window to fullscreen
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Make window background transparent (Windows specific)
    try:
        root.wm_attributes('-transparentcolor', 'black')
        root.configure(bg='black')
    except:
        pass
    
    # Keep window on top
    root.attributes('-topmost', True)
    
    print("=" * 60)
    print("REAL IMAGE DISPLAY - NO BACKGROUND")
    print("=" * 60)
    
    # Calculate cell size for 10x5 grid
    cell_width = screen_width // 10
    cell_height = screen_height // 5
    
    # Try to load the actual image from URL
    print("Loading image from URL...")
    photo = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=10)
        
        # Convert to PIL Image
        pil_image = Image.open(BytesIO(response.content))
        
        # Resize to fit cell
        pil_image = pil_image.resize((cell_width - 10, cell_height - 10), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Keep reference
        root.photo = photo
        
        print(f"Successfully loaded image: {pil_image.width}x{pil_image.height}")
        
    except Exception as e:
        print(f"Error loading image: {e}")
        print("Will use fallback image")
        photo = None
    
    # If image failed, create a simple fallback image
    if photo is None:
        # Create a simple colored image as fallback
        from PIL import ImageDraw
        fallback_img = Image.new('RGB', (cell_width - 10, cell_height - 10), color='red')
        draw = ImageDraw.Draw(fallback_img)
        draw.text((50, 50), "IMG", fill='white')
        photo = ImageTk.PhotoImage(fallback_img)
        root.photo = photo
    
    # Store positions for all 50 images (top-right to bottom-left)
    positions = []
    for i in range(50):
        row = i // 10  # 0-4
        col = 9 - (i % 10)  # 9-0 (right to left)
        x = col * cell_width + 5
        y = row * cell_height + 5
        positions.append((x, y))
    
    # Store image labels
    image_labels = []
    created_count = 0
    
    def create_next_image():
        nonlocal created_count
        
        if created_count >= 50:
            # Start destruction phase
            destroy_images()
            return
        
        # Create a label with the actual image
        label = tk.Label(root, image=photo, bg='black', bd=0)
        
        # Position it
        x, y = positions[created_count]
        label.place(x=x, y=y)
        
        # Add to list
        image_labels.append(label)
        created_count += 1
        
        print(f"Displayed image {created_count}/50 at position ({created_count})")
        
        # Remove oldest if we have more than 10
        if len(image_labels) > 10:
            oldest = image_labels.pop(0)
            oldest.destroy()
            print(f"  Removed oldest image (showing {len(image_labels)} images)")
        
        # Schedule next image
        if created_count < 50:
            root.after(50, create_next_image)
        else:
            # Wait then destroy remaining
            root.after(500, destroy_images)
    
    def destroy_images():
        """Destroy remaining images one by one"""
        if not image_labels:
            print("All images destroyed")
            root.after(1000, root.destroy)
            return
        
        # Destroy next image
        label = image_labels.pop(0)
        label.destroy()
        
        print(f"Destroyed image ({len(image_labels)} remaining)")
        
        # Schedule next destruction
        if image_labels:
            root.after(50, destroy_images)
        else:
            print("\n" + "=" * 50)
            print("PROGRAM COMPLETE")
            print("=" * 50)
            root.after(1000, root.destroy)
    
    # Start the display
    print("\nStarting image display in 2 seconds...")
    print("Images will appear from top-right to bottom-left")
    print("Only 10 images visible at a time")
    print("-" * 60)
    
    root.after(2000, create_next_image)
    
    # Exit handlers
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# Alternative using canvas for better transparency
def canvas_image_troll():
    """Use canvas to display images with better transparency control"""
    
    root = tk.Tk()
    root.title("")
    root.overrideredirect(True)
    
    # Get screen size
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+0+0")
    
    # Make window transparent
    try:
        root.attributes('-transparentcolor', 'black')
        root.configure(bg='black')
    except:
        pass
    
    root.attributes('-topmost', True)
    
    # Create canvas
    canvas = tk.Canvas(root, width=w, height=h, bg='black', highlightthickness=0)
    canvas.pack()
    
    print("Loading and displaying actual image...")
    
    # Load image
    photo = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=10)
        
        # Open and resize
        pil_img = Image.open(BytesIO(response.content))
        cell_w = w // 10
        cell_h = h // 5
        pil_img = pil_img.resize((cell_w - 20, cell_h - 20), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_img)
        root.photo = photo
        
    except Exception as e:
        print(f"Error: {e}")
        # Create fallback
        pil_img = Image.new('RGB', (100, 100), color='blue')
        photo = ImageTk.PhotoImage(pil_img)
        root.photo = photo
    
    # Store image objects
    image_objects = []
    created = 0
    
    # Pre-calculate positions
    positions = []
    cell_w = w // 10
    cell_h = h // 5
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)
        x = col * cell_w + 10
        y = row * cell_h + 10
        positions.append((x, y))
    
    def create_image():
        nonlocal created
        
        if created >= 50:
            remove_images()
            return
        
        # Create image on canvas
        x, y = positions[created]
        img_id = canvas.create_image(x, y, image=photo, anchor='nw')
        image_objects.append(img_id)
        
        created += 1
        print(f"Created image {created}/50")
        
        # Remove oldest if more than 10
        if len(image_objects) > 10:
            old_id = image_objects.pop(0)
            canvas.delete(old_id)
            print(f"  Removed oldest (showing {len(image_objects)})")
        
        # Schedule next
        if created < 50:
            root.after(50, create_image)
        else:
            root.after(500, remove_images)
    
    def remove_images():
        if not image_objects:
            print("Done - closing")
            root.after(1000, root.destroy)
            return
        
        img_id = image_objects.pop(0)
        canvas.delete(img_id)
        
        if image_objects:
            root.after(50, remove_images)
        else:
            root.after(1000, root.destroy)
    
    # Start
    root.after(1000, create_image)
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# SIMPLE WORKING VERSION
def simple_real_images():
    """Simple version that actually displays the image"""
    
    root = tk.Tk()
    root.title("")
    root.overrideredirect(True)
    
    # Fullscreen
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+0+0")
    
    # Try to make transparent
    try:
        root.wm_attributes('-transparentcolor', 'black')
    except:
        pass
    
    root.configure(bg='black')
    root.attributes('-topmost', True)
    
    print("Loading image...")
    
    # Load the actual image
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=10)
        
        # Open with PIL
        img = Image.open(BytesIO(response.content))
        
        # Resize for grid
        cell_w = w // 10
        cell_h = h // 5
        img = img.resize((cell_w - 10, cell_h - 10), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        root.photo = photo
        
        print(f"Image loaded: {img.width}x{img.height}")
        
    except Exception as e:
        print(f"Failed to load image: {e}")
        # Create a simple image as fallback
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        photo = ImageTk.PhotoImage(img)
        root.photo = photo
    
    # Create positions
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)
        x = col * (w // 10) + 5
        y = row * (h // 5) + 5
        positions.append((x, y))
    
    # Store labels
    labels = []
    count = 0
    
    def show_image():
        nonlocal count
        
        if count >= 50:
            # Destroy all
            destroy_all()
            return
        
        # Create and show image
        lbl = tk.Label(root, image=photo, bg='black')
        x, y = positions[count]
        lbl.place(x=x, y=y)
        
        labels.append(lbl)
        count += 1
        
        # Remove oldest if more than 10
        if len(labels) > 10:
            old = labels.pop(0)
            old.destroy()
        
        # Next image
        if count < 50:
            root.after(50, show_image)
        else:
            root.after(500, destroy_all)
    
    def destroy_all():
        while labels:
            lbl = labels.pop(0)
            lbl.destroy()
            root.update()
            time.sleep(0.05)
        
        root.after(1000, root.destroy)
    
    # Start
    root.after(1000, show_image)
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# Run the program
if __name__ == "__main__":
    # Install required packages
    try:
        import requests
        from PIL import Image, ImageTk
    except ImportError:
        import subprocess
        import sys
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pillow"])
        import requests
        from PIL import Image, ImageTk
    
    # Run the simple version
    simple_real_images()
