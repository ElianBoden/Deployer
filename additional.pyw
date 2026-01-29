import tkinter as tk
import requests
import time
import random

# NO UNICODE CHARACTERS - ASCII ONLY
def scary_image_invasion():
    """Fullscreen borderless window with images appearing one by one"""
    
    # Create window with NO BORDERS, NO TITLE BAR
    root = tk.Tk()
    root.title("")  # Empty title
    root.overrideredirect(True)  # Remove all window decorations
    root.attributes('-fullscreen', True)  # Fullscreen
    root.configure(bg='black')  # Black background
    root.attributes('-topmost', True)  # Always on top
    
    # Get screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Try to load image from URL
    photo = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=5)
        
        # Convert to tkinter PhotoImage
        from io import BytesIO
        import base64
        
        # Create PhotoImage from bytes
        img_data = response.content
        photo = tk.PhotoImage(data=base64.b64encode(img_data))
        root.tk_image = photo  # Keep reference
        
    except:
        # If image fails, we'll use text
        pass
    
    # Grid positions (10x5 = 50 images)
    cols = 10
    rows = 5
    
    # Calculate positions starting from TOP-RIGHT
    positions = []
    for i in range(50):
        row = i // cols  # 0 to 4
        col_in_row = i % cols  # 0 to 9
        col = cols - 1 - col_in_row  # Start from rightmost (9 to 0)
        
        # Calculate pixel position
        x = col * (screen_width // cols)
        y = row * (screen_height // rows)
        
        # Add random offset for creepiness
        x_offset = random.randint(-30, 30)
        y_offset = random.randint(-30, 30)
        
        positions.append((x + x_offset, y + y_offset))
    
    # Store all image labels
    image_labels = []
    current_image = 0
    
    def flash_white():
        """Quick white flash effect"""
        root.configure(bg='white')
        root.update()
        time.sleep(0.03)
        root.configure(bg='black')
        root.update()
    
    def show_next():
        """Display next image"""
        nonlocal current_image
        
        if current_image >= 50:
            # All images shown - add scary text
            scary_text = tk.Label(root, 
                                 text="LOOK BEHIND YOU", 
                                 font=("Arial", 48, "bold"),
                                 fg='red', 
                                 bg='black')
            scary_text.place(relx=0.5, rely=0.5, anchor='center')
            return
        
        # Occasionally flash the screen
        if random.random() < 0.15:
            flash_white()
        
        # Get position
        x, y = positions[current_image]
        
        # Create and show image
        if photo:
            label = tk.Label(root, image=photo, bg='black')
        else:
            # Fallback to text (no emoji - ASCII only)
            text_options = ["X", "O", "+", "*", "#", "@", "&", "%"]
            label = tk.Label(root, 
                           text=random.choice(text_options), 
                           font=("Arial", 60),
                           fg='white', 
                           bg='black')
        
        label.place(x=x, y=y)
        image_labels.append(label)
        
        current_image += 1
        
        # Random delay between 0.03 and 0.07 seconds
        delay = random.randint(30, 70)
        
        # Schedule next image
        if current_image < 50:
            root.after(delay, show_next)
        else:
            # All done - wait then show message
            root.after(1000, lambda: show_scary_message())
    
    def show_scary_message():
        """Show final scary message"""
        msg1 = tk.Label(root, 
                       text="YOU ARE NOT ALONE", 
                       font=("Courier", 36, "bold"),
                       fg='red', 
                       bg='black')
        msg1.place(relx=0.5, rely=0.4, anchor='center')
        
        msg2 = tk.Label(root,
                       text="PRESS ANY KEY TO ESCAPE", 
                       font=("Arial", 20),
                       fg='gray', 
                       bg='black')
        msg2.place(relx=0.5, rely=0.9, anchor='center')
        
        # Make message 2 blink
        def blink_msg():
            current_color = msg2.cget("fg")
            new_color = 'dark gray' if current_color == 'gray' else 'gray'
            msg2.config(fg=new_color)
            root.after(800, blink_msg)
        
        blink_msg()
    
    # Key bindings - only ESC actually exits
    def check_key(event):
        if event.keysym == 'Escape':
            root.destroy()
        else:
            # Wrong key - show error
            error = tk.Label(root, 
                            text="WRONG KEY!", 
                            font=("Arial", 20),
                            fg='red', 
                            bg='black')
            error.place(relx=0.5, rely=0.7, anchor='center')
            root.after(500, error.destroy)
    
    root.bind('<Key>', check_key)
    
    # Mouse click doesn't work immediately
    clicks_needed = 3
    click_count = 0
    
    def handle_click(event):
        nonlocal click_count
        click_count += 1
        
        if click_count >= clicks_needed:
            root.destroy()
        else:
            # Show how many clicks left
            hint = tk.Label(root,
                          text=f"{clicks_needed - click_count} MORE CLICKS", 
                          font=("Arial", 16),
                          fg='white', 
                          bg='black')
            hint.place(relx=0.5, rely=0.8, anchor='center')
            root.after(1000, hint.destroy)
    
    root.bind('<Button-1>', handle_click)
    
    # Start the invasion after 2 seconds
    def start():
        # Countdown in console (ASCII only)
        print("Starting in 3...")
        time.sleep(1)
        print("2...")
        time.sleep(1)
        print("1...")
        time.sleep(1)
        print("BEGIN!")
        
        # Initial flash
        flash_white()
        time.sleep(0.5)
        
        # Start showing images
        show_next()
    
    # Run start in thread
    import threading
    start_thread = threading.Thread(target=start)
    start_thread.daemon = True
    start_thread.start()
    
    # Start main loop
    root.mainloop()

# SIMPLEST VERSION - NO ERRORS
def simple_troll():
    """Even simpler - just works"""
    import tkinter as tk
    import requests
    
    # Create window
    window = tk.Tk()
    window.overrideredirect(True)
    window.attributes('-fullscreen', True)
    window.configure(bg='black')
    
    # Screen size
    w = window.winfo_screenwidth()
    h = window.winfo_screenheight()
    
    # Try to load image (but don't fail if it doesn't work)
    img = None
    try:
        url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
        response = requests.get(url, timeout=3)
        
        # Convert to PhotoImage
        from io import BytesIO
        import base64
        
        # Simple base64 encoding
        import base64
        img_data = response.content
        b64_data = base64.b64encode(img_data)
        img = tk.PhotoImage(data=b64_data)
        window.tk_image = img  # Keep reference
    except:
        pass
    
    # Create 50 positions
    positions = []
    for i in range(50):
        row = i // 10  # 0-4
        col = 9 - (i % 10)  # 9 to 0 (right to left)
        x = col * (w // 10)
        y = row * (h // 5)
        positions.append((x, y))
    
    # Counter
    count = 0
    labels = []
    
    def add_image():
        nonlocal count
        if count >= 50:
            return
        
        x, y = positions[count]
        
        if img:
            label = tk.Label(window, image=img, bg='black')
        else:
            # ASCII art if image fails
            label = tk.Label(window, text="[X]", font=("Arial", 40),
                           fg='white', bg='black')
        
        label.place(x=x, y=y)
        labels.append(label)
        count += 1
        
        # Next image in 50ms
        if count < 50:
            window.after(50, add_image)
        else:
            # Show exit hint
            hint = tk.Label(window, text="Press ESC", font=("Arial", 20),
                          fg='gray', bg='black')
            hint.place(relx=0.5, rely=0.95, anchor='center')
    
    # Start after 1 second
    window.after(1000, add_image)
    
    # Exit on ESC
    window.bind('<Escape>', lambda e: window.destroy())
    
    # Start
    window.mainloop()

# RUN IT
if __name__ == "__main__":
    # Try to install requests if needed
    try:
        import requests
    except:
        # Silent install attempt
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import requests
        except:
            pass
    
    # ASCII ONLY PRINT STATEMENTS
    print("=" * 60)
    print("IMAGE INVASION STARTING")
    print("Fullscreen window will appear")
    print("Images will cover your screen")
    print("=" * 60)
    
    # Run simple version (most reliable)
    simple_troll()
