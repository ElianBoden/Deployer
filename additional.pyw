import tkinter as tk
from tkinter import PhotoImage
import requests
from io import BytesIO
import random
import time

def create_creepy_fullscreen_troll():
    """Create a scary fullscreen troll with images appearing one by one"""
    
    # Create main window (NO TITLE BAR, NO BORDERS)
    root = tk.Tk()
    root.title("")  # Empty title
    root.overrideredirect(True)  # Remove window decorations completely
    root.attributes('-fullscreen', True)  # Fullscreen
    root.configure(bg='black')  # Start with black background
    
    # Force window to stay on top of everything
    root.attributes('-topmost', True)
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    print("=" * 60)
    print("CREEPY IMAGE INVASION ACTIVATED")
    print(f"Screen: {screen_width}x{screen_height}")
    print("Images will appear suddenly, one by one...")
    print("=" * 60)
    
    # Try to load the creepy image from URL
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Convert to tkinter PhotoImage
        img_data = BytesIO(response.content)
        photo = PhotoImage(data=img_data.read())
        root.tk_image = photo  # Keep reference
        
        img_width = photo.width()
        img_height = photo.height()
        print(f"Image loaded: {img_width}x{img_height}")
        
    except Exception as e:
        print(f"Error loading image: {e}")
        # Fallback to creepy emoji
        photo = None
        img_width = 150
        img_height = 150
    
    # Grid layout: 10 columns x 5 rows = 50 images
    cols = 10
    rows = 5
    
    # Calculate exact positions for each image
    positions = []
    for i in range(50):
        # Start from top-right (position 0 = top-right corner)
        row = i // cols  # Row index 0-4
        col_in_row = i % cols  # Column index in current row 0-9
        col = cols - 1 - col_in_row  # Reverse: start from rightmost column
        
        # Calculate exact pixel positions
        x = col * (screen_width // cols)
        y = row * (screen_height // rows)
        
        # Add some random offset for creepier effect
        x_offset = random.randint(-20, 20)
        y_offset = random.randint(-20, 20)
        
        positions.append((x + x_offset, y + y_offset))
    
    # List to hold all image labels
    image_labels = []
    
    # Counter for displayed images
    images_displayed = 0
    
    def flash_screen():
        """Quick flash effect before showing images"""
        root.configure(bg='white')
        root.update()
        time.sleep(0.05)
        root.configure(bg='black')
        root.update()
        time.sleep(0.1)
    
    def show_next_image():
        """Display next image with creepy effect"""
        nonlocal images_displayed
        
        if images_displayed >= 50:
            return
        
        # Occasionally flash the screen
        if random.random() < 0.1:  # 10% chance
            flash_screen()
        
        # Get position for this image
        x, y = positions[images_displayed]
        
        # Create the image label but DON'T show it yet
        if photo:
            label = tk.Label(root, image=photo, bg='black', bd=0)
        else:
            # Fallback: creepy emoji
            emojis = ["💀", "👻", "🎭", "🤡", "👁️", "🕷️", "🕸️"]
            emoji = random.choice(emojis)
            label = tk.Label(root, text=emoji, font=("Arial", 80), 
                           bg='black', fg='white')
        
        # Store reference
        image_labels.append(label)
        
        # SUDDEN APPEARANCE: Place it without animation
        label.place(x=x, y=y)
        
        # Occasionally make it blink
        if random.random() < 0.2:  # 20% chance
            def blink():
                label.config(bg='red')
                root.after(100, lambda: label.config(bg='black'))
            
            root.after(50, blink)
        
        images_displayed += 1
        print(f"Image {images_displayed}/50 appeared at ({x},{y})")
        
        # Random delay between 0.03 and 0.07 seconds for unpredictability
        delay = random.randint(30, 70)
        
        # Show next image
        if images_displayed < 50:
            root.after(delay, show_next_image)
        else:
            # All images displayed - add creepy text
            show_creepy_message()
    
    def show_creepy_message():
        """Display a creepy message when all images are shown"""
        time.sleep(0.5)
        
        # Create creepy text that fades in
        creepy_text = tk.Label(root, 
                              text="YOU CAN'T ESCAPE", 
                              font=("Courier", 48, "bold"),
                              fg='red', 
                              bg='black')
        creepy_text.place(relx=0.5, rely=0.4, anchor='center')
        
        # Second line
        creepy_text2 = tk.Label(root,
                               text="LOOK BEHIND YOU", 
                               font=("Courier", 36, "bold"),
                               fg='white', 
                               bg='black')
        creepy_text2.place(relx=0.5, rely=0.5, anchor='center')
        
        # Blinking exit hint (small and hard to see)
        exit_hint = tk.Label(root,
                            text="Press ANY KEY to exit", 
                            font=("Arial", 12),
                            fg='#222222',  # Very dark gray
                            bg='black')
        exit_hint.place(relx=0.5, rely=0.95, anchor='center')
        
        # Make hint blink subtly
        def blink_hint():
            current_color = exit_hint.cget("fg")
            new_color = '#555555' if current_color == '#222222' else '#222222'
            exit_hint.config(fg=new_color)
            root.after(1000, blink_hint)
        
        blink_hint()
    
    # Bind ALL keys to exit (makes it harder to find the right one)
    def try_to_exit(event=None):
        # Only ESC actually exits
        if event and hasattr(event, 'keysym') and event.keysym == 'Escape':
            print("Exiting...")
            root.destroy()
        else:
            # Wrong key - show error
            error_label = tk.Label(root, 
                                  text="WRONG KEY!", 
                                  font=("Arial", 24),
                                  fg='red', 
                                  bg='black')
            error_label.place(relx=0.5, rely=0.8, anchor='center')
            root.after(1000, error_label.destroy)
    
    root.bind('<Key>', try_to_exit)
    
    # Also bind mouse click (but make it not work immediately)
    click_count = 0
    def fake_exit(event=None):
        nonlocal click_count
        click_count += 1
        if click_count >= 5:  # Only exit after 5 clicks
            root.destroy()
        else:
            # Show fake closing message
            fake_msg = tk.Label(root, 
                               text=f"Closing... {5-click_count} clicks remaining", 
                               font=("Arial", 18),
                               fg='white', 
                               bg='black')
            fake_msg.place(relx=0.5, rely=0.9, anchor='center')
            root.after(1500, fake_msg.destroy)
    
    root.bind('<Button-1>', fake_exit)
    
    # Start the image invasion after 1 second
    def start_invasion():
        print("Starting in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("BEGIN!")
        flash_screen()
        show_next_image()
    
    # Run in separate thread to avoid blocking
    import threading
    invasion_thread = threading.Thread(target=start_invasion)
    invasion_thread.daemon = True
    invasion_thread.start()
    
    # Start the main loop
    root.mainloop()

# Ultra-simple version that just works
def simple_scary_troll():
    """Simpler version - less effects, just creepy appearance"""
    import tkinter as tk
    import requests
    
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    root.attributes('-topmost', True)
    
    # Load image
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=3)
        from io import BytesIO
        from PIL import Image, ImageTk
        import io
        
        img = Image.open(io.BytesIO(response.content))
        photo = ImageTk.PhotoImage(img)
        root.tk_image = photo
    except:
        photo = None
    
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    
    # Create all positions
    positions = []
    for i in range(50):
        row = i // 10
        col = 9 - (i % 10)  # Start from right
        x = col * (screen_w // 10)
        y = row * (screen_h // 5)
        positions.append((x, y))
    
    images_shown = 0
    labels = []
    
    def appear():
        nonlocal images_shown
        if images_shown >= 50:
            # Show creepy message
            msg = tk.Label(root, text="BOO!", font=("Arial", 72, "bold"),
                          fg='red', bg='black')
            msg.place(relx=0.5, rely=0.5, anchor='center')
            return
        
        x, y = positions[images_shown]
        
        if photo:
            label = tk.Label(root, image=photo, bg='black')
        else:
            label = tk.Label(root, text="👁️", font=("Arial", 60),
                           fg='white', bg='black')
        
        label.place(x=x, y=y)
        labels.append(label)
        images_shown += 1
        
        # Next image in 0.05 seconds
        if images_shown < 50:
            root.after(50, appear)
    
    # Start appearing after 1 second
    root.after(1000, appear)
    
    # Only ESC exits (hard to find)
    root.bind('<Escape>', lambda e: root.destroy())
    
    # Fake close on other keys
    def fake_close(event):
        if event.keysym != 'Escape':
            lbl = tk.Label(root, text="NOPE", font=("Arial", 30),
                          fg='white', bg='black')
            lbl.place(relx=0.5, rely=0.8, anchor='center')
            root.after(1000, lbl.destroy)
    
    root.bind('<Key>', fake_close)
    
    root.mainloop()

# Run it
if __name__ == "__main__":
    # Try to install required packages
    try:
        import requests
    except ImportError:
        import os
        os.system("pip install requests")
        import requests
    
    # Try PIL for better image handling
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Installing PIL...")
        import os
        os.system("pip install pillow")
    
    print("\n" + "⚠" * 60)
    print("WARNING: Creepy fullscreen troll will activate!")
    print("This will cover your entire screen with images.")
    print("Press ESC to exit (but it's hard to find!)")
    print("⚠" * 60 + "\n")
    
    import time
    time.sleep(3)  # Build suspense
    
    # Choose which version to run
    # simple_scary_troll()  # Simpler version
    create_creepy_fullscreen_troll()  # More creepy effects
