
import tkinter as tk
import urllib.request
from datetime import datetime
import sys
import random
import time
import threading
import math
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps

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
    
    # Store the original background color for flicker effect
    original_bg = '#000000'
    
    # Store original and modified images
    original_photo = None
    flicker_images = []  # Different versions for flickering
    current_image_label = None
    image_label = None  # Main image label
    
    # Try to load and display the image
    try:
        # Use a different, scarier image from Unsplash
        # This is a dark, eerie forest image
        image_url = "https://images.unsplash.com/photo-1562860149-691401a306f8?q=80&w=687&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        
        if image_url and image_url.strip():
            # Download image
            with urllib.request.urlopen(image_url) as response:
                image_data = response.read()
            
            # Convert to PhotoImage
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
            
            # Create different versions for flickering
            # 1. Original (slightly darker)
            original_image = image.copy()
            
            # 2. Bright red tint
            red_image = image.copy()
            r, g, b = red_image.split()
            r = r.point(lambda i: min(i * 1.8, 255))
            g = g.point(lambda i: i * 0.4)
            b = b.point(lambda i: i * 0.4)
            red_image = Image.merge('RGB', (r, g, b))
            
            # 3. High contrast black and white with red tint
            bw_image = image.copy().convert('L')
            bw_image = ImageEnhance.Contrast(bw_image).enhance(3.0)
            bw_image = bw_image.convert('RGB')
            r, g, b = bw_image.split()
            r = r.point(lambda i: min(i * 1.5, 255))
            bw_image = Image.merge('RGB', (r, g, b))
            
            # 4. Dark version (almost black)
            dark_image = ImageEnhance.Brightness(image).enhance(0.2)
            
            # 5. Inverted colors
            inverted_image = ImageOps.invert(image)
            r, g, b = inverted_image.split()
            g = g.point(lambda i: i * 0.3)
            b = b.point(lambda i: i * 0.3)
            inverted_image = Image.merge('RGB', (r, g, b))
            
            # 6. Blurred version
            blurred_image = image.filter(ImageFilter.GaussianBlur(radius=3))
            
            # 7. Extra red version
            extra_red_image = image.copy()
            r, g, b = extra_red_image.split()
            r = r.point(lambda i: min(i * 2.0, 255))
            g = g.point(lambda i: i * 0.2)
            b = b.point(lambda i: i * 0.2)
            extra_red_image = Image.merge('RGB', (r, g, b))
            
            # Convert all to PhotoImage
            original_photo = ImageTk.PhotoImage(original_image)
            flicker_images = [
                ImageTk.PhotoImage(red_image),
                ImageTk.PhotoImage(bw_image),
                ImageTk.PhotoImage(dark_image),
                ImageTk.PhotoImage(inverted_image),
                ImageTk.PhotoImage(blurred_image),
                ImageTk.PhotoImage(extra_red_image)
            ]
            
            # Create label to display image (fills entire window)
            image_label = tk.Label(window, image=original_photo, bg="#000000")
            image_label.image = original_photo  # Keep reference
            image_label.place(x=0, y=0, width=window_width, height=window_height)
            current_image_label = image_label
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Scary image loaded and displayed")
            
    except Exception as e:
        # If image loading fails, just create a solid red screen
        window.configure(bg='#8B0000')  # Dark red
        original_bg = '#8B0000'
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load image, using solid color: {e}")
    
    # Track active canvases to prevent interference
    active_canvases = []
    
    # IMAGE FLICKER EFFECT - Now flickers the image itself
    def image_flicker_effect():
        try:
            if window.winfo_exists() and image_label and flicker_images:
                # Randomly select a flicker image
                flicker_image = random.choice(flicker_images)
                
                # Change the image label to show flicker version
                image_label.config(image=flicker_image)
                image_label.image = flicker_image  # Keep reference
                
                # Random flicker duration (very short for strobe effect)
                flicker_duration = random.randint(30, 120)
                
                # Return to original image after flicker duration
                window.after(flicker_duration, return_to_original_image)
                
                # Schedule next flicker with random interval
                next_flicker = random.randint(50, 300)
                window.after(next_flicker, image_flicker_effect)
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Image flicker failed: {e}")
            # Try to continue flickering anyway
            if window.winfo_exists():
                window.after(100, image_flicker_effect)
    
    def return_to_original_image():
        try:
            if window.winfo_exists() and image_label and original_photo:
                image_label.config(image=original_photo)
                image_label.image = original_photo
        except:
            pass
    
    # Start image flicker effect
    if image_label and flicker_images:
        window.after(500, image_flicker_effect)
    else:
        # Fallback to canvas flicker if no image
        def intense_flicker():
            try:
                if window.winfo_exists():
                    # More varied and intense colors
                    colors = ['#000000', '#330000', '#660000', '#990000', '#CC0000', '#FF0000']
                    flicker_color = random.choice(colors)
                    
                    # Create a semi-transparent overlay for flicker
                    flicker_canvas = tk.Canvas(window, bg='', highlightthickness=0)
                    flicker_canvas.place(x=0, y=0, width=window_width, height=window_height)
                    flicker_canvas.create_rectangle(0, 0, window_width, window_height, 
                                                   fill=flicker_color, outline='', stipple='gray50')
                    active_canvases.append(flicker_canvas)
                    
                    # Remove after very short time for strobe effect
                    window.after(random.randint(30, 100), 
                               lambda fc=flicker_canvas: remove_canvas(fc))
                    
                    # Schedule next flicker
                    window.after(random.randint(50, 200), intense_flicker)
            except:
                pass
        
        intense_flicker()
    
    # IMPROVED EYE EFFECT WITH MOVEMENT AND BLINKING
    class ScaryEye:
        def __init__(self, canvas, x, y, size):
            self.canvas = canvas
            self.x = x
            self.y = y
            self.size = size
            self.blink_state = 0  # 0=open, 1=half, 2=closed
            self.direction_x = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
            self.direction_y = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
            
            # Draw eye with glow effect
            self.glow = canvas.create_oval(x-size*1.5, y-size*0.75, 
                                           x+size*1.5, y+size*0.75,
                                           fill='#FF4444', outline='', width=0)
            self.white = canvas.create_oval(x-size, y-size//2, 
                                           x+size, y+size//2,
                                           fill='#FFFFFF', outline='', width=0)
            pupil_size = size // 3
            self.pupil = canvas.create_oval(x-pupil_size, y-pupil_size//2,
                                           x+pupil_size, y+pupil_size//2,
                                           fill='#000000', outline='', width=0)
            
        def update_position(self):
            # Move eye slightly
            self.x += self.direction_x
            self.y += self.direction_y
            
            # Bounce off edges
            if self.x < self.size*2 or self.x > window_width - self.size*2:
                self.direction_x *= -1
            if self.y < self.size*2 or self.y > window_height - self.size*2:
                self.direction_y *= -1
            
            # Update eye position
            self.canvas.coords(self.glow, 
                              self.x-self.size*1.5, self.y-self.size*0.75,
                              self.x+self.size*1.5, self.y+self.size*0.75)
            self.canvas.coords(self.white,
                              self.x-self.size, self.y-self.size//2,
                              self.x+self.size, self.y+self.size//2)
            pupil_size = self.size // 3
            self.canvas.coords(self.pupil,
                              self.x-pupil_size, self.y-pupil_size//2,
                              self.x+pupil_size, self.y+pupil_size//2)
        
        def blink(self):
            if self.blink_state == 0:  # Start blinking
                # Make eye half closed
                self.canvas.coords(self.white,
                                  self.x-self.size, self.y-self.size//4,
                                  self.x+self.size, self.y+self.size//4)
                pupil_size = self.size // 6
                self.canvas.coords(self.pupil,
                                  self.x-pupil_size, self.y-pupil_size//4,
                                  self.x+pupil_size, self.y+pupil_size//4)
                self.blink_state = 1
            elif self.blink_state == 1:  # Fully close
                self.canvas.coords(self.white,
                                  self.x-self.size, self.y-2,
                                  self.x+self.size, self.y+2)
                self.canvas.coords(self.pupil,
                                  self.x-2, self.y-2,
                                  self.x+2, self.y+2)
                self.blink_state = 2
            else:  # Open again
                self.canvas.coords(self.white,
                                  self.x-self.size, self.y-self.size//2,
                                  self.x+self.size, self.y+self.size//2)
                pupil_size = self.size // 3
                self.canvas.coords(self.pupil,
                                  self.x-pupil_size, self.y-pupil_size//2,
                                  self.x+pupil_size, self.y+pupil_size//2)
                self.blink_state = 0
    
    eyes = []
    
    def add_eye_effect():
        try:
            if window.winfo_exists():
                # Create a canvas for drawing effects
                canvas = tk.Canvas(window, bg='', highlightthickness=0)
                canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(canvas)
                
                # Add several "eyes" that appear randomly
                for _ in range(random.randint(2, 4)):
                    x = random.randint(50, window_width - 50)
                    y = random.randint(50, window_height - 50)
                    size = random.randint(15, 40)
                    
                    eye = ScaryEye(canvas, x, y, size)
                    eyes.append((eye, canvas))
                
                # Make eyes move and blink
                def animate_eyes():
                    if window.winfo_exists():
                        for eye, canv in eyes[:]:
                            if canv.winfo_exists():
                                eye.update_position()
                                if random.random() < 0.1:  # 10% chance to blink
                                    eye.blink()
                        
                        # Schedule next animation frame
                        window.after(50, animate_eyes)
                
                # Start eye animation
                animate_eyes()
                
                # Make eyes disappear after random time
                window.after(random.randint(2000, 5000), 
                           lambda c=canvas: remove_canvas(c))
        except:
            pass
    
    def remove_canvas(canvas):
        try:
            if canvas.winfo_exists():
                canvas.destroy()
            if canvas in active_canvases:
                active_canvases.remove(canvas)
            # Remove any eyes associated with this canvas
            global eyes
            eyes = [(eye, canv) for eye, canv in eyes if canv != canvas]
        except:
            pass
    
    # Trigger eye effects at random intervals
    def trigger_eyes():
        try:
            if window.winfo_exists():
                add_eye_effect()
                window.after(random.randint(1500, 4000), trigger_eyes)
        except:
            pass
    
    # Start eye effects after a delay
    window.after(800, trigger_eyes)
    
    # ENHANCED GLITCH EFFECTS
    def enhanced_glitch_effect():
        try:
            if window.winfo_exists():
                # Create temporary glitch canvas
                glitch_canvas = tk.Canvas(window, bg='', highlightthickness=0)
                glitch_canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(glitch_canvas)
                
                # Different types of glitches
                glitch_type = random.choice(['lines', 'static', 'blocks', 'wave'])
                
                if glitch_type == 'lines':
                    # Horizontal and vertical lines
                    for _ in range(random.randint(3, 8)):
                        if random.random() < 0.5:  # Horizontal
                            x1 = random.randint(0, window_width)
                            y1 = random.randint(0, window_height)
                            width = random.randint(30, 150)
                            height = random.randint(1, 4)
                            color = random.choice(['#FF0000', '#00FF00', '#0000FF'])
                            glitch_canvas.create_rectangle(x1, y1, x1+width, y1+height, 
                                                          fill=color, outline='', width=0)
                        else:  # Vertical
                            x1 = random.randint(0, window_width)
                            y1 = random.randint(0, window_height)
                            width = random.randint(1, 4)
                            height = random.randint(30, 150)
                            color = random.choice(['#FF0000', '#00FF00', '#0000FF'])
                            glitch_canvas.create_rectangle(x1, y1, x1+width, y1+height, 
                                                          fill=color, outline='', width=0)
                
                elif glitch_type == 'static':
                    # TV static effect
                    for _ in range(random.randint(50, 150)):
                        x1 = random.randint(0, window_width)
                        y1 = random.randint(0, window_height)
                        size = random.randint(1, 3)
                        color = random.choice(['#FFFFFF', '#888888', '#000000'])
                        glitch_canvas.create_rectangle(x1, y1, x1+size, y1+size, 
                                                      fill=color, outline='', width=0)
                
                elif glitch_type == 'blocks':
                    # Blocky glitch
                    for _ in range(random.randint(10, 30)):
                        x1 = random.randint(0, window_width)
                        y1 = random.randint(0, window_height)
                        size = random.randint(10, 40)
                        color = random.choice(['#FF0000', '#00FF00', '#0000FF', '#FFFFFF'])
                        glitch_canvas.create_rectangle(x1, y1, x1+size, y1+size, 
                                                      fill=color, outline='', width=0)
                
                elif glitch_type == 'wave':
                    # Wave distortion effect
                    for y in range(0, window_height, 10):
                        offset = int(math.sin(y / 50.0 * math.pi) * 20)
                        color = random.choice(['#FF0000', '#00FFFF', '#FFFF00'])
                        glitch_canvas.create_rectangle(0+offset, y, window_width+offset, y+5, 
                                                      fill=color, outline='', width=0)
                
                # Remove glitch after very short time
                window.after(random.randint(60, 200), 
                           lambda gc=glitch_canvas: remove_canvas(gc))
        except:
            pass
        
        # Schedule next glitch if window exists
        if window.winfo_exists():
            window.after(random.randint(300, 1500), enhanced_glitch_effect)
    
    # Start enhanced glitch effects
    window.after(300, enhanced_glitch_effect)
    
    # SCARY TEXT APPEARANCE
    def scary_text_effect():
        try:
            if window.winfo_exists():
                # Create canvas for text
                text_canvas = tk.Canvas(window, bg='', highlightthickness=0)
                text_canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(text_canvas)
                
                # Scary messages
                messages = [
                    "GET OUT", "HELP ME", "BEHIND YOU", "DON'T LOOK",
                    "THEY'RE HERE", "I SEE YOU", "RUN", "IT'S TOO LATE"
                ]
                
                # Add random text
                for _ in range(random.randint(1, 3)):
                    x = random.randint(20, window_width - 100)
                    y = random.randint(20, window_height - 40)
                    message = random.choice(messages)
                    
                    # Create text with shadow for creepy effect
                    text_canvas.create_text(x+2, y+2, text=message, 
                                           fill='#880000', font=('Arial', random.randint(20, 40), 'bold'))
                    text_canvas.create_text(x, y, text=message, 
                                           fill='#FF0000', font=('Arial', random.randint(20, 40), 'bold'))
                
                # Remove after delay
                window.after(random.randint(1000, 3000), 
                           lambda tc=text_canvas: remove_canvas(tc))
        except:
            pass
        
        # Schedule next text effect
        if window.winfo_exists():
            window.after(random.randint(4000, 8000), scary_text_effect)
    
    # Start text effects after delay
    window.after(2000, scary_text_effect)
    
    # IMAGE DISTORTION EFFECT
    def image_distortion_effect():
        try:
            if window.winfo_exists() and image_label and original_photo:
                # Create a temporary distorted version of the image
                if flicker_images:
                    # Pick a random distortion
                    distortion_type = random.choice(['red_flash', 'blur', 'invert'])
                    
                    if distortion_type == 'red_flash':
                        image_label.config(image=flicker_images[0])  # Red version
                    elif distortion_type == 'blur':
                        image_label.config(image=flicker_images[4])  # Blurred version
                    elif distortion_type == 'invert':
                        image_label.config(image=flicker_images[3])  # Inverted version
                    
                    # Keep distortion for a moment
                    window.after(random.randint(80, 200), return_to_original_image)
        except:
            pass
        
        # Schedule next distortion
        if window.winfo_exists():
            window.after(random.randint(1000, 3000), image_distortion_effect)
    
    # Start image distortion effect
    if image_label and flicker_images:
        window.after(2500, image_distortion_effect)
    
    # BLOOD DRIP EFFECT
    def blood_drip_effect():
        try:
            if window.winfo_exists():
                canvas = tk.Canvas(window, bg='', highlightthickness=0)
                canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(canvas)
                
                # Create multiple drips
                drips = []
                for _ in range(random.randint(3, 8)):
                    x = random.randint(10, window_width - 10)
                    drips.append({'x': x, 'y': 0, 'length': 0, 'max_length': random.randint(30, 150)})
                
                def animate_drips(frame=0):
                    if not canvas.winfo_exists():
                        return
                    
                    canvas.delete('all')
                    
                    for drip in drips:
                        # Draw blood drip
                        drip_length = min(drip['length'], drip['max_length'])
                        if drip_length > 0:
                            # Main drip line
                            canvas.create_line(drip['x'], drip['y'], 
                                             drip['x'], drip['y'] + drip_length,
                                             fill='#8B0000', width=3)
                            
                            # Drip end (bulb)
                            if drip['length'] >= drip['max_length'] and frame % 10 < 5:
                                canvas.create_oval(drip['x']-4, drip['y']+drip_length-4,
                                                  drip['x']+4, drip['y']+drip_length+4,
                                                  fill='#FF0000', outline='')
                        
                        # Grow drip
                        if drip['length'] < drip['max_length']:
                            drip['length'] += random.randint(1, 3)
                    
                    # Continue animation
                    if any(drip['length'] < drip['max_length'] for drip in drips) or frame < 100:
                        window.after(50, lambda: animate_drips(frame+1))
                    else:
                        window.after(1000, lambda c=canvas: remove_canvas(c))
                
                # Start drip animation
                animate_drips()
        except:
            pass
        
        # Schedule next blood drip
        if window.winfo_exists():
            window.after(random.randint(8000, 15000), blood_drip_effect)
    
    # Start blood drip effect
    window.after(5000, blood_drip_effect)
    
    # Add low-frequency ominous hum (simulated with console message)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Playing ominous frequency: 13Hz...")
    
    # INTENSE CLOSE EFFECT WITH IMAGE FLICKER
    def close_window():
        # Add intense closing sequence with rapid image flickering
        try:
            if window.winfo_exists():
                def final_flicker_sequence(count=0):
                    if count >= 15:  # Flicker 15 times before closing
                        final_destroy()
                        return
                    
                    # Rapid flicker between original and red version
                    if image_label and flicker_images:
                        if count % 2 == 0:
                            image_label.config(image=flicker_images[0])  # Red version
                        else:
                            image_label.config(image=original_photo)
                    
                    # Schedule next flicker
                    window.after(80, lambda: final_flicker_sequence(count + 1))
                
                # Start final flicker sequence
                final_flicker_sequence()
        except:
            final_destroy()
    
    def final_destroy():
        try:
            # Clean up all canvases first
            for canvas in active_canvases[:]:
                try:
                    if canvas.winfo_exists():
                        canvas.destroy()
                except:
                    pass
            
            if window.winfo_exists():
                window.destroy()
        except:
            pass
    
    # Schedule window to close after 15 seconds (longer for effects)
    window.after(15000, close_window)
    
    # Print to console
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] SCARY WINDOW ACTIVATED - IMAGE FLICKER VERSION")
    print(f"[{current_time}] [INFO] Screen size: {screen_width}x{screen_height}")
    print(f"[{current_time}] [INFO] Window size: {window_width}x{window_height}")
    print(f"[{current_time}] [INFO] Window will close in 15 seconds")
    
    # Bind escape key to close window (for safety)
    def on_escape(event):
        final_destroy()
    
    window.bind('<Escape>', on_escape)
    
    # Run the window
    try:
        window.mainloop()
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Window error: {e}")
    
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] Window deactivated")

if __name__ == "__main__":
    try:
        # Try to import required modules
        try:
            from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Installing Pillow...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--quiet"])
            from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
        
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Script interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
