import tkinter as tk
import requests
import time

def create_sliding_transparent_troll():
    """Borderless window with transparent images, sliding window effect"""
    
    # Create window
    root = tk.Tk()
    root.title("")
    
    # Remove ALL window decorations - NO TAB, NO BORDER
    root.overrideredirect(True)
    
    # Get screen size and make fullscreen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Use black background instead of white for creepy effect
    root.configure(bg='black')
    
    # Keep window on top
    root.attributes('-topmost', True)
    
    print("=" * 60)
    print("TRANSPARENT IMAGE SLIDING WINDOW - NO BACKGROUND")
    print("=" * 60)
    
    # Calculate cell size for 10x5 grid
    cell_width = screen_width // 10
    cell_height = screen_height // 5
    
    # Try to load image with transparency support
    img = None
    try:
        from io import BytesIO
        from PIL import Image, ImageTk
        
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Open image and resize
        pil_image = Image.open(BytesIO(response.content))
        
        # Create transparency by making white pixels transparent
        pil_image = pil_image.convert("RGBA")
        datas = pil_image.getdata()
        
        new_data = []
        for item in datas:
            # Make white pixels transparent (adjust threshold as needed)
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                new_data.append((255, 255, 255, 0))  # Fully transparent
            else:
                new_data.append(item)
        
        pil_image.putdata(new_data)
        
        # Resize to fit cell
        pil_image = pil_image.resize((cell_width - 10, cell_height - 10), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        img = ImageTk.PhotoImage(pil_image)
        root.tk_image = img
        
        print(f"Image loaded with transparency")
        
    except Exception as e:
        print(f"Could not load image: {e}")
        img = None
    
    # Store positions for all 50 images (top-right to bottom-left)
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)  # Start from rightmost column
        x = col * cell_width + 5
        y = row * cell_height + 5
        positions.append((x, y))
    
    # Sliding window variables
    image_queue = []  # Stores current visible images (max 10)
    total_created = 0  # How many images created so far (0-50)
    is_destroying = False  # Flag for destruction phase
    destruction_index = 0  # Index for destruction phase
    
    def create_next_image():
        """Create and show next image in sequence"""
        nonlocal total_created
        
        if total_created >= 50:
            # All images created, start destruction phase
            start_destruction()
            return
        
        # Create image label
        if img:
            label = tk.Label(root, image=img, bg='black')
        else:
            # Fallback if image loading failed
            label = tk.Label(root, text=str(total_created + 1), 
                           font=("Arial", 20), fg='red', bg='black')
        
        # Place at calculated position
        x, y = positions[total_created]
        label.place(x=x, y=y)
        
        # Add to queue
        image_queue.append(label)
        
        print(f"Image {total_created + 1} created")
        total_created += 1
        
        # If we have more than 10 images, destroy oldest
        if len(image_queue) > 10:
            oldest = image_queue.pop(0)
            oldest.destroy()
            print(f"  Destroyed oldest (visible: {len(image_queue)})")
        
        # Schedule next creation if not done
        if total_created < 50:
            root.after(50, create_next_image)
        else:
            # All created, wait a moment then start destruction
            root.after(500, start_destruction)
    
    def start_destruction():
        """Start destroying the last 10 images one by one"""
        nonlocal is_destroying
        
        if not image_queue:
            print("No images to destroy")
            return
        
        is_destroying = True
        print("\n" + "-" * 40)
        print("DESTRUCTION PHASE: Destroying last 10 images...")
        print("-" * 40)
        
        # Start destroying images one by one
        destroy_next_image()
    
    def destroy_next_image():
        """Destroy next image in the queue"""
        nonlocal destruction_index
        
        if not image_queue:
            print("All images destroyed!")
            # Wait and then close window
            root.after(1000, root.destroy)
            return
        
        # Destroy the first image in queue
        label = image_queue.pop(0)
        label.destroy()
        
        destruction_index += 1
        print(f"Destroyed image {destruction_index}/10")
        
        # Continue destroying if queue not empty
        if image_queue:
            root.after(50, destroy_next_image)
        else:
            print("\n" + "=" * 40)
            print("ALL IMAGES DESTROYED - WINDOW WILL CLOSE")
            print("=" * 40)
            root.after(1000, root.destroy)
    
    # Start creating images after 1 second delay
    root.after(1000, create_next_image)
    
    # Exit handlers
    def exit_program(event=None):
        print("\nProgram terminated by user")
        root.destroy()
    
    root.bind('<Escape>', exit_program)
    root.bind('<Control-c>', exit_program)
    
    # Add hidden exit hint (barely visible)
    exit_hint = tk.Label(root, text="ESC", font=("Arial", 8), 
                        fg='#222222', bg='black')
    exit_hint.place(x=screen_width - 30, y=5)
    
    print("\nPROGRAM STARTED:")
    print("1. Images will appear one by one (0.05s interval)")
    print("2. After 10 images, oldest destroyed as new ones appear")
    print("3. After all 50 created, last 10 destroyed one by one")
    print("4. Window will close automatically")
    print("\nPress ESC to exit early")
    print("=" * 60)
    
    # Start main loop
    root.mainloop()

# Alternative simpler version without PIL
def simple_troll_no_background():
    """Version without PIL dependency"""
    
    root = tk.Tk()
    root.title("")
    root.overrideredirect(True)
    
    # Fullscreen
    w = root.winfo_screenwidth()
    h = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+0+0")
    root.configure(bg='black')
    
    # Calculate positions
    cell_w = w // 10
    cell_h = h // 5
    
    # Try to load image
    photo = None
    try:
        import base64
        import io
        
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Simple PhotoImage without transparency
        photo = tk.PhotoImage(data=base64.b64encode(response.content))
        root.photo = photo
        
    except:
        photo = None
    
    # Store positions
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)
        x = col * cell_w + 5
        y = row * cell_h + 5
        positions.append((x, y))
    
    # Queue for images
    queue = []
    created = 0
    
    def add_image():
        nonlocal created
        
        if created >= 50:
            # Start destroying
            destroy_all()
            return
        
        # Create image
        if photo:
            label = tk.Label(root, image=photo, bg='black')
        else:
            # Create red rectangle instead
            canvas = tk.Canvas(root, width=cell_w-10, height=cell_h-10, 
                             bg='black', highlightthickness=0)
            canvas.create_rectangle(0, 0, cell_w-10, cell_h-10, 
                                  fill='red', outline='')
            label = canvas
        
        x, y = positions[created]
        label.place(x=x, y=y)
        
        queue.append(label)
        created += 1
        
        # Remove oldest if we have more than 10
        if len(queue) > 10:
            old = queue.pop(0)
            old.destroy()
        
        # Schedule next
        if created < 50:
            root.after(50, add_image)
        else:
            # Wait then destroy all
            root.after(500, destroy_all)
    
    def destroy_all():
        """Destroy all remaining images one by one"""
        if not queue:
            root.after(1000, root.destroy)
            return
        
        # Destroy one image
        label = queue.pop(0)
        label.destroy()
        
        # Schedule next destruction
        if queue:
            root.after(50, destroy_all)
        else:
            # All destroyed, close window
            root.after(1000, root.destroy)
    
    # Start
    root.after(1000, add_image)
    
    # Exit
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# Run the program
if __name__ == "__main__":
    # Install required packages if needed
    try:
        import requests
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    # Try to use first version with transparency
    create_sliding_transparent_troll()
    
    # If that fails, use simple version:
    # simple_troll_no_background()
