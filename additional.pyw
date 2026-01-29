
import tkinter as tk
import requests
import time

def create_transparent_troll():
    """Window with transparent background - only images visible"""
    
    # Create window
    root = tk.Tk()
    root.title("")
    
    # Remove ALL window decorations
    root.overrideredirect(True)
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Make window COMPLETELY TRANSPARENT
    root.attributes('-alpha', 0.01)  # Almost invisible window
    root.configure(bg='black')
    
    # Keep window on top
    root.attributes('-topmost', True)
    
    print("=" * 60)
    print("TRANSPARENT WINDOW - ONLY IMAGES VISIBLE")
    print("=" * 60)
    
    # Calculate cell size for grid
    cell_width = screen_width // 10
    cell_height = screen_height // 5
    
    # Try to load image
    img = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        from io import BytesIO
        from PIL import Image, ImageTk
        
        # Open and resize image
        pil_image = Image.open(BytesIO(response.content))
        pil_image = pil_image.resize((cell_width - 4, cell_height - 4), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        img = ImageTk.PhotoImage(pil_image)
        root.tk_image = img
        
    except Exception as e:
        print(f"Image error: {e}")
        img = None
    
    # Store positions
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)  # Start from rightmost
        x = col * cell_width + 2
        y = row * cell_height + 2
        positions.append((x, y))
    
    # Create special windows for each image (not labels)
    image_windows = []
    created = 0
    
    def create_next_image():
        nonlocal created
        
        if created >= 50:
            # Start destruction phase
            destroy_images()
            return
        
        # Create a SEPARATE TRANSPARENT WINDOW for this image
        img_win = tk.Toplevel(root)
        img_win.overrideredirect(True)  # No decorations
        img_win.attributes('-topmost', True)
        
        # Position it
        x, y = positions[created]
        img_win.geometry(f"{cell_width-4}x{cell_height-4}+{x}+{y}")
        
        # Make it transparent except for the image
        img_win.attributes('-transparentcolor', 'black')
        img_win.configure(bg='black')
        
        # Add the image
        if img:
            label = tk.Label(img_win, image=img, bg='black')
        else:
            # Fallback: create a canvas with color
            canvas = tk.Canvas(img_win, width=cell_width-4, height=cell_height-4, 
                             bg='black', highlightthickness=0)
            colors = ['red', 'blue', 'green', 'yellow', 'purple']
            canvas.create_rectangle(0, 0, cell_width-4, cell_height-4, 
                                  fill=colors[created % len(colors)])
            canvas.create_text((cell_width-4)//2, (cell_height-4)//2, 
                             text=str(created+1), font=("Arial", 20), fill='white')
            label = canvas
        
        label.pack(fill=tk.BOTH, expand=True)
        
        # Store window reference
        image_windows.append(img_win)
        created += 1
        
        print(f"Created image {created}/50 at ({x},{y})")
        
        # Remove oldest if more than 10
        if len(image_windows) > 10:
            old_win = image_windows.pop(0)
            old_win.destroy()
            print(f"  Destroyed oldest (visible: {len(image_windows)})")
        
        # Schedule next
        if created < 50:
            root.after(50, create_next_image)
        else:
            # Wait then destroy all
            root.after(500, destroy_images)
    
    def destroy_images():
        """Destroy remaining images one by one"""
        if not image_windows:
            print("All images destroyed - closing")
            root.after(1000, root.destroy)
            return
        
        # Destroy next window
        win = image_windows.pop(0)
        win.destroy()
        
        print(f"Destroyed image ({len(image_windows)} remaining)")
        
        # Schedule next destruction
        if image_windows:
            root.after(50, destroy_images)
        else:
            print("\n" + "=" * 50)
            print("COMPLETE - ALL IMAGES DESTROYED")
            print("=" * 50)
            root.after(1000, root.destroy)
    
    # Start
    print("Starting in 2 seconds...")
    root.after(2000, create_next_image)
    
    # Exit on ESC
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.mainloop()

# Even simpler approach: Create individual windows
def individual_image_windows():
    """Create separate windows for each image"""
    
    import tkinter as tk
    import time
    
    # Store all windows
    windows = []
    
    # Create main control window (hidden)
    control = tk.Tk()
    control.withdraw()  # Hide it
    
    screen_width = control.winfo_screenwidth()
    screen_height = control.winfo_screenheight()
    
    cell_width = screen_width // 10
    cell_height = screen_height // 5
    
    # Load image once
    photo = None
    try:
        from io import BytesIO
        from PIL import Image, ImageTk
        import requests
        
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        pil_img = Image.open(BytesIO(response.content))
        pil_img = pil_img.resize((cell_width - 10, cell_height - 10), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(pil_img)
        
    except:
        photo = None
    
    # Create all positions
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)
        x = col * cell_width + 5
        y = row * cell_height + 5
        positions.append((x, y))
    
    created = 0
    visible_windows = []
    
    def create_window():
        nonlocal created
        
        if created >= 50:
            # Start destroying
            destroy_windows()
            return
        
        # Create a new window for this image
        win = tk.Toplevel(control)
        win.overrideredirect(True)
        win.attributes('-topmost', True)
        
        # Set window to be transparent except for image
        win.attributes('-transparentcolor', 'black')
        
        # Position
        x, y = positions[created]
        win.geometry(f"{cell_width-10}x{cell_height-10}+{x}+{y}")
        
        # Add image or fallback
        if photo:
            lbl = tk.Label(win, image=photo, bg='black')
        else:
            # Create colored square
            colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']
            color = colors[created % len(colors)]
            lbl = tk.Label(win, bg=color, text=str(created+1), 
                          font=("Arial", 16), fg='white')
        
        lbl.pack(fill=tk.BOTH, expand=True)
        
        windows.append(win)
        visible_windows.append(win)
        created += 1
        
        # Remove oldest if more than 10
        if len(visible_windows) > 10:
            old = visible_windows.pop(0)
            old.destroy()
        
        # Schedule next
        if created < 50:
            control.after(50, create_window)
        else:
            control.after(500, destroy_windows)
    
    def destroy_windows():
        """Destroy visible windows one by one"""
        if not visible_windows:
            print("All windows destroyed")
            control.after(1000, control.destroy)
            return
        
        win = visible_windows.pop(0)
        win.destroy()
        
        if visible_windows:
            control.after(50, destroy_windows)
        else:
            control.after(1000, control.destroy)
    
    # Start
    control.after(1000, create_window)
    
    # Exit
    control.bind('<Escape>', lambda e: control.destroy())
    
    control.mainloop()

# ULTRA SIMPLE: Just create 50 individual popup windows
def simple_popup_images():
    """Create 50 separate popup windows as images"""
    
    import tkinter as tk
    
    # Main control (hidden)
    master = tk.Tk()
    master.withdraw()
    
    # Get screen size
    w = master.winfo_screenwidth()
    h = master.winfo_screenheight()
    
    # Cell size
    cell_w = w // 10
    cell_h = h // 5
    
    # Create windows list
    windows = []
    created = 0
    
    def make_window():
        nonlocal created
        
        if created >= 50:
            # Start removing
            remove_windows()
            return
        
        # Create popup window
        win = tk.Toplevel(master)
        win.overrideredirect(True)
        
        # Position
        row = created // 10
        col = 9 - (created % 10)
        x = col * cell_w + 10
        y = row * cell_h + 10
        
        win.geometry(f"{cell_w-20}x{cell_h-20}+{x}+{y}")
        
        # Make it look like just an image
        win.configure(bg='black')
        
        # Add a canvas with color
        canvas = tk.Canvas(win, width=cell_w-20, height=cell_h-20, 
                          bg='black', highlightthickness=0)
        colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff']
        color = colors[created % len(colors)]
        canvas.create_rectangle(0, 0, cell_w-20, cell_h-20, fill=color)
        canvas.create_text((cell_w-20)//2, (cell_h-20)//2, 
                          text=str(created+1), font=("Arial", 24), fill='white')
        canvas.pack()
        
        windows.append(win)
        created += 1
        
        # Remove oldest if more than 10
        if len(windows) > 10:
            old = windows.pop(0)
            old.destroy()
        
        # Schedule next
        if created < 50:
            master.after(50, make_window)
        else:
            master.after(500, remove_windows)
    
    def remove_windows():
        if not windows:
            master.after(1000, master.destroy)
            return
        
        win = windows.pop(0)
        win.destroy()
        
        if windows:
            master.after(50, remove_windows)
        else:
            master.after(1000, master.destroy)
    
    # Start
    master.after(1000, make_window)
    
    # Exit on ESC
    def exit_all(e=None):
        for win in windows:
            try:
                win.destroy()
            except:
                pass
        master.destroy()
    
    master.bind('<Escape>', exit_all)
    
    master.mainloop()

# Run the simplest version
if __name__ == "__main__":
    print("CREATING IMAGE-ONLY DISPLAY")
    print("No background window - only images will appear")
    print("-" * 50)
    
    # Try to run the simple version
    simple_popup_images()
