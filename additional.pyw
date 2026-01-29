import tkinter as tk
import requests
import time
from io import BytesIO
from PIL import Image, ImageTk
import argparse
import sys

# Configuration presets
CONFIG_PRESETS = {
    'default': {
        'image_urls': [
            "https://images.unsplash.com/photo-1562860149-691401a306f8?q=80&w=687&auto=format&fit=crop",
            "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        ]
    },
    'alternative': {
        'image_urls': [
            "https://images.unsplash.com/photo-1562860149-691401a306f8?q=80&w=687&auto=format&fit=crop"
        ]
    }
}

def simple_real_images(image_url=None):
    """Simple version that actually displays the image"""
    
    if image_url is None:
        # Use the first URL from default preset
        image_url = CONFIG_PRESETS['default']['image_urls'][0]
    
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
    
    print(f"Loading image from: {image_url}")
    
    # Load the actual image
    try:
        response = requests.get(image_url, timeout=10)
        
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
        
        print(f"Displayed image {count}/50")
        
        # Remove oldest if more than 10
        if len(labels) > 10:
            old = labels.pop(0)
            old.destroy()
            print(f"Removed oldest image ({len(labels)} visible)")
        
        # Next image
        if count < 50:
            root.after(50, show_image)
        else:
            root.after(500, destroy_all)
    
    def destroy_all():
        print("Destroying all images...")
        while labels:
            lbl = labels.pop(0)
            lbl.destroy()
            root.update()
            time.sleep(0.05)
        
        print("All images destroyed. Closing in 1 second...")
        root.after(1000, root.destroy)
    
    # Start
    root.after(1000, show_image)
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# Run the program
if __name__ == "__main__":
    # Install required packages if needed
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
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Image Display Script')
    parser.add_argument('--url', type=str, help='Direct image URL to use')
    parser.add_argument('--preset', type=str, default='default', 
                       choices=list(CONFIG_PRESETS.keys()),
                       help=f'Preset configuration to use (default: default)')
    
    args = parser.parse_args()
    
    # Get the image URL
    if args.url:
        # Use the direct URL if provided
        image_url = args.url
        print(f"Using direct URL: {image_url}")
    else:
        # Use the first URL from the selected preset
        try:
            image_url = CONFIG_PRESETS[args.preset]['image_urls'][0]
            print(f"Using preset '{args.preset}': {image_url}")
        except KeyError as e:
            print(f"Error: Preset '{args.preset}' does not have 'image_urls' key")
            print(f"Available keys in preset '{args.preset}': {list(CONFIG_PRESETS[args.preset].keys())}")
            print(f"Falling back to default preset...")
            image_url = CONFIG_PRESETS['default']['image_urls'][0]
        except IndexError:
            print(f"Error: Preset '{args.preset}' has no image URLs")
            print(f"Falling back to default preset...")
            image_url = CONFIG_PRESETS['default']['image_urls'][0]
    
    # Run the simple version with the selected image
    simple_real_images(image_url)
