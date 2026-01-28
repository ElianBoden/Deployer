
# additional.pyw - Scary full-screen image display
import tkinter as tk
import urllib.request
from datetime import datetime
import sys
import random
import time

def main():
    # Create the main window
    window = tk.Tk()
    
    # Get screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate 50% of screen size (centered)
    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.5)
    
    # Calculate position to center the window
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    
    # Set window geometry
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Remove window decorations and make it borderless
    window.overrideredirect(True)  # No title bar, borders, or controls
    window.configure(bg='#000000')
    
    # Make window always on top
    window.attributes('-topmost', True)
    
    # Try to load and display the image
    try:
        # Use a different, scarier image from Unsplash
        # This is a dark, eerie forest image
        image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        
        # Download image
        with urllib.request.urlopen(image_url) as response:
            image_data = response.read()
        
        # Convert to PhotoImage
        from PIL import Image, ImageTk, ImageEnhance
        import io
        
        # Load image
        image = Image.open(io.BytesIO(image_data))
        
        # Make image darker and more ominous
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(0.4)  # 40% brightness
        
        # Increase contrast for more dramatic effect
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.8)  # 180% contrast
        
        # Add a red tint for horror effect
        r, g, b = image.split()
        # Boost red channel
        r = r.point(lambda i: i * 1.3 if i > 60 else i)
        # Reduce green and blue
        g = g.point(lambda i: i * 0.7)
        b = b.point(lambda i: i * 0.7)
        image = Image.merge('RGB', (r, g, b))
        
        # Resize image to fill the window completely
        image = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(image)
        
        # Create label to display image (fills entire window)
        image_label = tk.Label(window, image=photo, bg="#000000")
        image_label.image = photo
        image_label.place(x=0, y=0, width=window_width, height=window_height)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Scary image loaded and displayed")
        
    except Exception as e:
        # If image loading fails, just create a solid red screen
        window.configure(bg='#8B0000')  # Dark red
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load image, using solid color: {e}")
    
    # Add subtle flicker effect for horror
    def flicker():
        colors = ['#000000', '#1a0000', '#330000', '#4d0000']
        window.configure(bg=random.choice(colors))
        window.after(random.randint(50, 300), flicker)
    
    # Start flicker effect
    flicker()
    
    # Add a barely visible face/eye effect in random positions
    def add_eye_effect():
        try:
            # Create a canvas for drawing effects
            canvas = tk.Canvas(window, bg='', highlightthickness=0)
            canvas.place(x=0, y=0, width=window_width, height=window_height)
            
            # Add several "eyes" that appear randomly
            for _ in range(3):
                x = random.randint(50, window_width - 50)
                y = random.randint(50, window_height - 50)
                size = random.randint(10, 30)
                
                # Draw eye (white part)
                canvas.create_oval(x-size, y-size//2, x+size, y+size//2, 
                                  fill='#FFFFFF', outline='', width=0)
                
                # Draw pupil
                pupil_size = size // 3
                canvas.create_oval(x-pupil_size, y-pupil_size//2, 
                                  x+pupil_size, y+pupil_size//2, 
                                  fill='#000000', outline='', width=0)
                
                # Make eyes disappear after random time
                window.after(random.randint(500, 2000), 
                           lambda c=canvas, i=_: c.delete('all'))
        except:
            pass
    
    # Trigger eye effects at random intervals
    def trigger_eyes():
        add_eye_effect()
        window.after(random.randint(1000, 3000), trigger_eyes)
    
    # Start eye effects after a delay
    window.after(1000, trigger_eyes)
    
    # Add random screen glitch effect
    def glitch_effect():
        try:
            # Create temporary glitch rectangles
            glitch_canvas = tk.Canvas(window, bg='', highlightthickness=0)
            glitch_canvas.place(x=0, y=0, width=window_width, height=window_height)
            
            # Add random glitch lines
            for _ in range(random.randint(2, 5)):
                x1 = random.randint(0, window_width)
                y1 = random.randint(0, window_height)
                width = random.randint(20, 100)
                height = random.randint(2, 5)
                glitch_canvas.create_rectangle(x1, y1, x1+width, y1+height, 
                                              fill='#FF0000', outline='', width=0)
            
            # Remove glitch after very short time
            window.after(random.randint(50, 150), glitch_canvas.destroy)
        except:
            pass
        
        # Schedule next glitch
        window.after(random.randint(500, 2000), glitch_effect)
    
    # Start glitch effects
    window.after(500, glitch_effect)
    
    # Add low-frequency ominous hum (simulated with console message)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Playing ominous frequency: 13Hz...")
    
    # Function to close window after 5 seconds
    def close_window():
        # Add final effect before closing
        try:
            # Flash red before closing
            original_color = window.cget('bg')
            window.configure(bg='#FF0000')
            window.update()
            time.sleep(0.1)
            window.configure(bg='#000000')
            window.update()
            time.sleep(0.1)
        except:
            pass
        
        window.destroy()
    
    # Schedule window to close after 5 seconds
    window.after(10000, close_window)
    
    # Print to console
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] Scary window activated")
    print(f"[{current_time}] [INFO] Screen size: {screen_width}x{screen_height}")
    print(f"[{current_time}] [INFO] Window size: {window_width}x{window_height}")
    print(f"[{current_time}] [INFO] Window will close in 5 seconds")
    
    # Bind escape key to close window (for safety)
    def on_escape(event):
        window.destroy()
    
    window.bind('<Escape>', on_escape)
    
    # Run the window
    try:
        window.mainloop()
    except:
        pass
    
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] Window deactivated")

if __name__ == "__main__":
    try:
        # Try to import required modules
        try:
            from PIL import Image, ImageTk, ImageEnhance
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Installing Pillow...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--quiet"])
            from PIL import Image, ImageTk, ImageEnhance
        
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Script interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {e}")
        sys.exit(1)
