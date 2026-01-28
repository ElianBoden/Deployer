import tkinter as tk
import urllib.request
from datetime import datetime
import sys
import random
import time
import threading
import math
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps, ImageDraw
import colorsys

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
    
    # Store original window settings for animation
    original_geometry = {
        'width': window_width,
        'height': window_height,
        'x': x_position,
        'y': y_position
    }
    
    # Set initial window geometry
    window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    
    # Remove window decorations and make it borderless
    window.overrideredirect(True)  # No title bar, borders, or controls
    window.configure(bg='#000000')
    
    # Make window always on top
    window.attributes('-topmost', True)
    
    # ===========================================
    # SCARIER IMAGE SETUP
    # ===========================================
    
    # Store original and modified images
    original_photo = None
    flicker_images = []  # Different versions for flickering
    image_label = None  # Main image label
    
    # For smooth animations
    animation_active = True
    shake_offset_x = 0
    shake_offset_y = 0
    pulse_scale = 1.0
    animation_time = 0
    full_screen_image = None
    full_screen_photo = None
    
    # DISTORTION EFFECTS
    distortion_active = False
    distortion_strength = 0
    
    # SCARY TEXT OVERLAYS
    scary_texts = ["DON'T LOOK", "BEHIND YOU", "IT'S HERE", "GET OUT", "RUN", "TOO LATE", "IT SEES YOU"]
    current_text_index = 0
    text_overlay = None
    
    # Try to load and display the image
    try:
        # Use a much scarier image
        image_url = "https://images.unsplash.com/photo-1509248961158-e54f6934749c?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        
        if image_url and image_url.strip():
            # Download image
            with urllib.request.urlopen(image_url) as response:
                image_data = response.read()
            
            # Convert to PhotoImage
            import io
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Create high-res version for full screen scare
            full_screen_image = image.copy()
            
            # EXTREME DARKENING AND DISTORTION
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(0.3)  # 30% brightness (darker!)
            
            # Extreme contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.2)  # 220% contrast
            
            # BLOOD RED TINT
            r, g, b = image.split()
            # Boost red channel dramatically
            r = r.point(lambda i: min(i * 1.8, 255))
            # Severely reduce green and blue
            g = g.point(lambda i: i * 0.3)
            b = b.point(lambda i: i * 0.3)
            image = Image.merge('RGB', (r, g, b))
            
            # Add subtle "burn" effect at edges
            width, height = image.size
            for y in range(height):
                for x in range(width):
                    dist_from_center = ((x - width/2)**2 + (y - height/2)**2)**0.5
                    max_dist = ((width/2)**2 + (height/2)**2)**0.5
                    darkness = 1 - (dist_from_center / max_dist) * 0.7
                    pixel = image.getpixel((x, y))
                    new_pixel = tuple(int(c * darkness) for c in pixel)
                    image.putpixel((x, y), new_pixel)
            
            # Resize image to fill the window completely
            image = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            
            # Create different versions for flickering
            # 1. Original (slightly darker)
            original_image = image.copy()
            
            # 2. GLOWING EYES VERSION
            eyes_image = image.copy()
            draw = ImageDraw.Draw(eyes_image)
            # Add faint eye glows
            for i in range(3):
                eye_x = random.randint(50, window_width-50)
                eye_y = random.randint(50, window_height-50)
                eye_size = random.randint(20, 40)
                draw.ellipse([eye_x-eye_size, eye_y-eye_size//2,
                             eye_x+eye_size, eye_y+eye_size//2],
                            fill=(255, 50, 50, 100))
            
            # 3. EXTREME RED VERSION
            red_image = image.copy()
            r, g, b = red_image.split()
            r = r.point(lambda i: 255 if i > 100 else i*2)
            g = g.point(lambda i: i * 0.1)
            b = b.point(lambda i: i * 0.1)
            red_image = Image.merge('RGB', (r, g, b))
            
            # 4. NEGATIVE VERSION
            negative_image = ImageOps.invert(image)
            r, g, b = negative_image.split()
            g = g.point(lambda i: i * 0.2)
            b = b.point(lambda i: i * 0.2)
            negative_image = Image.merge('RGB', (r, g, b))
            
            # 5. GHOSTLY GREEN VERSION
            green_image = image.copy().convert('L')
            green_image = green_image.convert('RGB')
            r, g, b = green_image.split()
            r = r.point(lambda i: i * 0.3)
            g = g.point(lambda i: min(i * 2.5, 255))
            b = b.point(lambda i: i * 0.3)
            green_image = Image.merge('RGB', (r, g, b))
            
            # 6. DISTORTED VERSION
            distorted_image = image.copy()
            distorted_image = distorted_image.filter(ImageFilter.GaussianBlur(radius=2))
            distorted_image = distorted_image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            # 7. BLOOD SPLATTER VERSION
            blood_image = image.copy()
            for i in range(10):
                x = random.randint(0, window_width)
                y = random.randint(0, window_height)
                size = random.randint(5, 20)
                draw = ImageDraw.Draw(blood_image)
                draw.ellipse([x-size, y-size, x+size, y+size], 
                           fill=(139, 0, 0, 128))
            
            # 8. STATIC VERSION
            static_image = image.copy()
            pixels = static_image.load()
            for i in range(int(window_width * window_height * 0.1)):
                x = random.randint(0, window_width-1)
                y = random.randint(0, window_height-1)
                pixels[x, y] = (random.randint(200, 255), 
                              random.randint(0, 50), 
                              random.randint(0, 50))
            
            # Convert all to PhotoImage
            original_photo = ImageTk.PhotoImage(original_image)
            flicker_images = [
                ImageTk.PhotoImage(eyes_image),
                ImageTk.PhotoImage(red_image),
                ImageTk.PhotoImage(negative_image),
                ImageTk.PhotoImage(green_image),
                ImageTk.PhotoImage(distorted_image),
                ImageTk.PhotoImage(blood_image),
                ImageTk.PhotoImage(static_image)
            ]
            
            # Create label to display image (fills entire window)
            image_label = tk.Label(window, image=original_photo, bg="#000000")
            image_label.image = original_photo  # Keep reference
            image_label.place(x=0, y=0, width=window_width, height=window_height)
            
            # Add text overlay
            text_overlay = tk.Label(window, text="", font=("Arial", 16, "bold"),
                                  bg='#000000', fg='#FF0000')
            text_overlay.place(relx=0.5, rely=0.9, anchor="center")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Terrifying image loaded and displayed")
            
    except Exception as e:
        # If image loading fails, create a demonic pattern
        window.configure(bg='#000000')
        canvas = tk.Canvas(window, bg='#000000', highlightthickness=0)
        canvas.place(x=0, y=0, width=window_width, height=window_height)
        
        # Create a creepy pattern
        for i in range(0, window_width, 20):
            for j in range(0, window_height, 20):
                color = '#%02x%02x%02x' % (
                    min(255, 100 + int((i+j) % 255)),
                    max(0, 50 - int((i*j) % 100)),
                    max(0, 30 - int((i^j) % 70))
                )
                canvas.create_oval(i-2, j-2, i+2, j+2, fill=color, outline='')
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load image: {e}")
    
    # Track active canvases to prevent interference
    active_canvases = []
    
    # ===========================================
    # MORE INTENSE SMOOTH ANIMATIONS
    # ===========================================
    
    def update_smooth_animations():
        """Update smooth shaking and pulsing animations with more intensity"""
        nonlocal shake_offset_x, shake_offset_y, pulse_scale, animation_time
        nonlocal distortion_active, distortion_strength, current_text_index
        
        if not animation_active or not window.winfo_exists():
            return
        
        # Time progression
        animation_time += 0.04  # Slightly faster
        
        # VIOLENT SHAKING with multiple frequencies
        shake1 = math.sin(animation_time * 12) * 3  # Fast violent jitter
        shake2 = math.sin(animation_time * 4) * 6   # Medium strong shake
        shake3 = math.sin(animation_time * 0.7) * 8 # Slow powerful drift
        
        # Combine shakes - more violent
        shake_offset_x = int(shake1 * 0.4 + shake2 * 0.6 + shake3 * 0.3)
        shake_offset_y = int(math.cos(animation_time * 9) * 3 + 
                           math.sin(animation_time * 3) * 5 + 
                           math.cos(animation_time * 0.6) * 7)
        
        # HEARTBEAT-LIKE PULSING
        heartbeat = abs(math.sin(animation_time * 2))  # Faster heartbeat
        violent_pulse = math.sin(animation_time * 1.5) * math.sin(animation_time * 0.3)
        
        # Intense pulsing (up to 10% size change)
        pulse_scale = 1.0 + heartbeat * 0.05 + violent_pulse * 0.05
        
        # Calculate new window size with pulse
        new_width = int(original_geometry['width'] * pulse_scale)
        new_height = int(original_geometry['height'] * pulse_scale)
        
        # Calculate new position (centered with shake offset)
        new_x = original_geometry['x'] + shake_offset_x - (new_width - original_geometry['width']) // 2
        new_y = original_geometry['y'] + shake_offset_y - (new_height - original_geometry['height']) // 2
        
        # Apply geometry update
        window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
        
        # Update image size if it exists
        if image_label and image_label.winfo_exists():
            image_label.place(x=0, y=0, width=new_width, height=new_height)
        
        # DISTORTION EFFECT (occasional)
        if random.random() < 0.1:  # 10% chance per frame
            distortion_active = True
            distortion_strength = random.uniform(0.5, 1.5)
        
        if distortion_active:
            distortion_strength *= 0.9  # Decay
            if distortion_strength < 0.1:
                distortion_active = False
        
        # Update scary text overlay (every 2 seconds)
        if int(animation_time * 10) % 20 == 0:
            if text_overlay:
                current_text_index = (current_text_index + 1) % len(scary_texts)
                text_overlay.config(text=scary_texts[current_text_index])
                # Flash the text
                text_overlay.config(fg='#FF0000')
                window.after(100, lambda: text_overlay.config(fg='#880000') if text_overlay else None)
        
        # Schedule next animation frame
        window.after(16, update_smooth_animations)  # ~60 FPS
    
    # Start smooth animations
    window.after(100, update_smooth_animations)
    
    # ===========================================
    # EXTREME FLICKER EFFECT
    # ===========================================
    
    last_flicker_time = 0
    flicker_cooldown = 0.2  # Faster flickers
    
    def image_flicker_effect():
        """Extreme image flicker effect"""
        nonlocal last_flicker_time
        
        try:
            current_time = time.time()
            
            # Skip if too soon
            if current_time - last_flicker_time < flicker_cooldown:
                window.after(random.randint(50, 200), image_flicker_effect)
                return
            
            if window.winfo_exists() and image_label and flicker_images:
                # Random flicker with different probabilities
                flicker_type = random.random()
                if flicker_type < 0.3:  # 30% chance: extreme red
                    flicker_image = flicker_images[1]
                elif flicker_type < 0.5:  # 20% chance: eyes version
                    flicker_image = flicker_images[0]
                elif flicker_type < 0.7:  # 20% chance: negative
                    flicker_image = flicker_images[2]
                elif flicker_type < 0.85:  # 15% chance: blood
                    flicker_image = flicker_images[5]
                else:  # 15% chance: static
                    flicker_image = flicker_images[6]
                
                # Change the image
                image_label.config(image=flicker_image)
                image_label.image = flicker_image
                
                last_flicker_time = current_time
                
                # VERY short flicker for strobe effect
                flicker_duration = random.randint(20, 50)  # 20-50ms
                
                # Return to original
                window.after(flicker_duration, return_to_original_image)
                
                # Schedule next flicker with random interval (very frequent)
                next_flicker = random.randint(100, 400)
                window.after(next_flicker, image_flicker_effect)
        except Exception as e:
            if window.winfo_exists():
                window.after(200, image_flicker_effect)
    
    def return_to_original_image():
        """Return to original image after flicker"""
        try:
            if window.winfo_exists() and image_label and original_photo:
                image_label.config(image=original_photo)
                image_label.image = original_photo
        except:
            pass
    
    # Start extreme flicker effect
    if image_label and flicker_images:
        window.after(500, image_flicker_effect)
    
    # ===========================================
    # DEMONIC EYE EFFECT
    # ===========================================
    
    class DemonicEye:
        def __init__(self, canvas, x, y, size):
            self.canvas = canvas
            self.x = x
            self.y = y
            self.size = size
            self.blink_timer = 0
            self.blink_state = 0
            self.direction_x = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
            self.direction_y = random.choice([-1, 1]) * random.uniform(0.5, 2.0)
            self.pupil_target_x = x
            self.pupil_target_y = y
            
            # Draw DEMONIC eye with glow
            self.glow = canvas.create_oval(x-size*2, y-size*0.8,
                                          x+size*2, y+size*0.8,
                                          fill='#FF0000', outline='#FF4444', width=1)
            self.white = canvas.create_oval(x-size*1.5, y-size*0.6,
                                          x+size*1.5, y+size*0.6,
                                          fill='#FFFFFF', outline='', width=0)
            
            # Veins on the eye
            for i in range(3):
                offset = random.uniform(-size*0.3, size*0.3)
                self.canvas.create_line(x-size*0.8, y+offset,
                                       x+size*0.8, y+offset,
                                       fill='#FF6666', width=1)
            
            pupil_size = size // 2
            self.pupil = canvas.create_oval(x-pupil_size, y-pupil_size//1.5,
                                           x+pupil_size, y+pupil_size//1.5,
                                           fill='#000000', outline='#330000', width=1)
            
            # Reflection spot
            self.reflection = canvas.create_oval(x-pupil_size//3, y-pupil_size//4,
                                                x-pupil_size//6, y-pupil_size//8,
                                                fill='#FFFFFF', outline='', width=0)
            
        def update_position(self):
            # Update pupil target (follows mouse or random)
            if random.random() < 0.3:
                self.pupil_target_x = self.x + random.uniform(-self.size*0.5, self.size*0.5)
                self.pupil_target_y = self.y + random.uniform(-self.size*0.3, self.size*0.3)
            
            # Smooth pupil movement
            self.x += (self.pupil_target_x - self.x) * 0.3
            self.y += (self.pupil_target_y - self.y) * 0.3
            
            # Update all eye parts
            self.canvas.coords(self.glow,
                              self.x-self.size*2, self.y-self.size*0.8,
                              self.x+self.size*2, self.y+self.size*0.8)
            self.canvas.coords(self.white,
                              self.x-self.size*1.5, self.y-self.size*0.6,
                              self.x+self.size*1.5, self.y+self.size*0.6)
            
            pupil_size = self.size // 2
            pupil_x = self.x + (self.pupil_target_x - self.x) * 0.5
            pupil_y = self.y + (self.pupil_target_y - self.y) * 0.5
            self.canvas.coords(self.pupil,
                              pupil_x-pupil_size, pupil_y-pupil_size//1.5,
                              pupil_x+pupil_size, pupil_y+pupil_size//1.5)
            
            # Update reflection
            self.canvas.coords(self.reflection,
                              pupil_x-pupil_size//3, pupil_y-pupil_size//4,
                              pupil_x-pupil_size//6, pupil_y-pupil_size//8)
            
            # Random color change for glow
            if random.random() < 0.1:
                colors = ['#FF0000', '#FF3300', '#FF0066', '#990000']
                self.canvas.itemconfig(self.glow, fill=random.choice(colors))
        
        def update_blink(self):
            self.blink_timer += 1
            if self.blink_timer >= random.randint(40, 80):
                self.blink_timer = 0
                self.blink_state = (self.blink_state + 1) % 4
                
                if self.blink_state == 1:  # Half closed
                    self.canvas.coords(self.white,
                                      self.x-self.size*1.5, self.y-self.size*0.3,
                                      self.x+self.size*1.5, self.y+self.size*0.3)
                elif self.blink_state == 2:  # Mostly closed
                    self.canvas.coords(self.white,
                                      self.x-self.size*1.5, self.y-2,
                                      self.x+self.size*1.5, self.y+2)
                elif self.blink_state == 3:  // Twitching
                    self.canvas.coords(self.white,
                                      self.x-self.size*1.5, self.y-self.size*0.4,
                                      self.x+self.size*1.5, self.y+self.size*0.1)
                else:  # Open
                    self.canvas.coords(self.white,
                                      self.x-self.size*1.5, self.y-self.size*0.6,
                                      self.x+self.size*1.5, self.y+self.size*0.6)
    
    demonic_eyes = []
    
    def add_demonic_eye():
        try:
            if window.winfo_exists():
                canvas = tk.Canvas(window, bg='', highlightthickness=0)
                canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(canvas)
                
                # Add multiple demonic eyes
                eye_count = random.randint(2, 4)
                for _ in range(eye_count):
                    x = random.randint(60, window_width - 60)
                    y = random.randint(60, window_height - 60)
                    size = random.randint(20, 35)
                    
                    eye = DemonicEye(canvas, x, y, size)
                    demonic_eyes.append((eye, canvas))
                
                def animate_demonic_eyes():
                    if window.winfo_exists():
                        for eye, canv in demonic_eyes[:]:
                            if canv.winfo_exists():
                                eye.update_position()
                                eye.update_blink()
                        
                        window.after(80, animate_demonic_eyes)
                
                animate_demonic_eyes()
                
                # Remove after shorter time
                window.after(random.randint(2000, 4000),
                           lambda c=canvas: remove_canvas(c))
        except:
            pass
    
    def remove_canvas(canvas):
        try:
            if canvas.winfo_exists():
                canvas.destroy()
            if canvas in active_canvases:
                active_canvases.remove(canvas)
            global demonic_eyes
            demonic_eyes = [(eye, canv) for eye, canv in demonic_eyes if canv != canvas]
        except:
            pass
    
    def trigger_demonic_eyes():
        try:
            if window.winfo_exists():
                add_demonic_eye()
                # More frequent appearances
                window.after(random.randint(2000, 4000), trigger_demonic_eyes)
        except:
            pass
    
    # Start demonic eye effects
    window.after(1000, trigger_demonic_eyes)
    
    # ===========================================
    # CREEPY BLOOD DRIP EFFECT
    # ===========================================
    
    blood_drops = []
    
    def create_blood_drip():
        if not window.winfo_exists():
            return
        
        try:
            canvas = tk.Canvas(window, bg='', highlightthickness=0)
            canvas.place(x=0, y=0, width=window_width, height=window_height)
            active_canvases.append(canvas)
            
            # Create blood drip
            start_x = random.randint(50, window_width - 50)
            drip_length = random.randint(30, 80)
            drip_width = random.randint(2, 5)
            
            # Main drip line
            drip = canvas.create_line(start_x, 0, start_x, drip_length,
                                     fill='#8B0000', width=drip_width, smooth=True)
            
            # Blood drop at the end
            drop = canvas.create_oval(start_x-3, drip_length-3,
                                     start_x+3, drip_length+3,
                                     fill='#FF0000', outline='')
            
            # Animate drip falling
            def animate_drip(y_pos=0):
                if y_pos > window_height:
                    canvas.destroy()
                    if canvas in active_canvases:
                        active_canvases.remove(canvas)
                    return
                
                canvas.coords(drip, start_x, y_pos, start_x, y_pos + drip_length)
                canvas.coords(drop, start_x-3, y_pos + drip_length-3,
                             start_x+3, y_pos + drip_length+3)
                
                # Trail effect
                if random.random() < 0.3:
                    trail = canvas.create_oval(start_x-1, y_pos-1,
                                              start_x+1, y_pos+1,
                                              fill='#660000', outline='')
                    # Fade out trail
                    def fade_trail(obj):
                        for alpha in range(100, 0, -20):
                            if window.winfo_exists():
                                try:
                                    color = '#%02x0000' % int(alpha * 2.55)
                                    canvas.itemconfig(obj, fill=color)
                                    window.update()
                                except:
                                    break
                            time.sleep(0.01)
                        try:
                            canvas.delete(obj)
                        except:
                            pass
                    
                    threading.Thread(target=fade_trail, args=(trail,), daemon=True).start()
                
                window.after(50, lambda: animate_drip(y_pos + 10))
            
            animate_drip()
            
            # Remove canvas after animation
            window.after(5000, lambda: remove_canvas(canvas))
        except:
            pass
    
    def trigger_blood_drips():
        if window.winfo_exists():
            if random.random() < 0.4:  # 40% chance
                create_blood_drip()
            window.after(random.randint(1000, 3000), trigger_blood_drips)
    
    window.after(2000, trigger_blood_drips)
    
    # ===========================================
    # FINAL TERRIFYING SCARE SEQUENCE - 12 SECONDS
    # ===========================================
    
    def terrifying_final_scare():
        """Final terrifying scare - 12 second version"""
        nonlocal animation_active, full_screen_photo
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [SCARE] Starting TERRIFYING final scare!")
        
        # Stop normal animations
        animation_active = False
        
        # Clear all effects
        for canvas in active_canvases[:]:
            try:
                if canvas.winfo_exists():
                    canvas.destroy()
            except:
                pass
        active_canvases.clear()
        
        def scare_sequence(step=0):
            if not window.winfo_exists():
                return
            
            if step == 0:
                # Phase 1: VIOLENT SHAKING WITH BLOOD
                print("[SCARE] Phase 1: Violent shaking with blood")
                violent_shake_with_blood(0)
                
            elif step == 1:
                # Phase 2: EPILEPTIC FLICKER
                print("[SCARE] Phase 2: Epileptic flicker")
                epileptic_flicker(0)
                
            elif step == 2:
                // Phase 3: FULL SCREEN DEMONIC TRANSFORMATION
                print("[SCARE] Phase 3: Demonic full screen!")
                demonic_full_screen()
                
            elif step == 3:
                // Phase 4: FINAL JUMPSCARE HOLD
                print("[SCARE] Phase 4: Final jumpscare")
                window.after(800, final_demonic_destroy)
        
        def violent_shake_with_blood(count=0):
            if count >= 18:  // Slightly longer shaking
                window.after(200, lambda: scare_sequence(1))
                return
            
            // EXTREME shaking
            shake_x = random.randint(-40, 40)
            shake_y = random.randint(-30, 30)
            
            current_width = window.winfo_width()
            current_height = window.winfo_height()
            current_x = window.winfo_x()
            current_y = window.winfo_y()
            
            window.geometry(f"{current_width}x{current_height}+{current_x+shake_x}+{current_y+shake_y}")
            
            // Blood red flicker during shake
            if image_label and flicker_images and count % 3 == 0:
                image_label.config(image=flicker_images[1])  // Extreme red
            elif image_label and count % 3 == 1:
                image_label.config(image=flicker_images[5])  // Blood
            
            // Add random blood drips during shake
            if random.random() < 0.4:
                create_blood_drip()
            
            window.after(40, lambda: violent_shake_with_blood(count + 1))
        
        def epileptic_flicker(count=0):
            if count >= 15:
                window.after(150, lambda: scare_sequence(2))
                return
            
            // Ultra-fast random flicker
            if image_label and flicker_images:
                flicker_image = random.choice(flicker_images)
                image_label.config(image=flicker_image)
                image_label.image = flicker_image
            
            // Flash window background
            if count % 2 == 0:
                window.configure(bg='#FF0000')
            else:
                window.configure(bg='#000000')
            
            window.after(40, lambda: epileptic_flicker(count + 1))
        
        def demonic_full_screen():
            """Demonic transformation to full screen"""
            if not window.winfo_exists():
                return
            
            // Create ultimate demonic image
            if full_screen_image:
                demonic_image = full_screen_image.copy()
                
                // Extreme demonic enhancements
                // 1. Invert and red tint
                demonic_image = ImageOps.invert(demonic_image)
                r, g, b = demonic_image.split()
                r = r.point(lambda i: min(i * 3.0, 255))
                g = g.point(lambda i: i * 0.1)
                b = b.point(lambda i: i * 0.1)
                demonic_image = Image.merge('RGB', (r, g, b))
                
                // 2. Add demonic eyes
                draw = ImageDraw.Draw(demonic_image)
                for i in range(5):
                    eye_x = random.randint(100, screen_width-100)
                    eye_y = random.randint(100, screen_height-100)
                    eye_size = random.randint(40, 80)
                    // Glowing red eyes
                    for j in range(3):
                        glow_size = eye_size * (1 + j * 0.3)
                        draw.ellipse([eye_x-glow_size, eye_y-glow_size//2,
                                     eye_x+glow_size, eye_y+glow_size//2],
                                    fill=(255, 50, 50, 50 + j*20))
                
                // 3. Resize to full screen
                demonic_image = demonic_image.resize((screen_width, screen_height),
                                                    Image.Resampling.LANCZOS)
                
                full_screen_photo = ImageTk.PhotoImage(demonic_image)
            
            // Get current window position
            start_width = window.winfo_width()
            start_height = window.winfo_height()
            start_x = window.winfo_x()
            start_y = window.winfo_y()
            
            // Target: full screen
            target_width = screen_width
            target_height = screen_height
            target_x = 0
            target_y = 0
            
            // Animate expansion
            def demonic_expand(frame=0):
                if frame > 30:
                    // Final frame: set to full screen
                    window.geometry(f"{target_width}x{target_height}+{target_x}+{target_y}")
                    
                    // Switch to demonic image
                    if full_screen_photo and image_label:
                        image_label.config(image=full_screen_photo)
                        image_label.image = full_screen_photo
                        image_label.place(x=0, y=0, width=target_width, height=target_height)
                    
                    // Add final text overlay
                    if text_overlay:
                        text_overlay.config(text="IT HAS YOU", font=("Arial", 32, "bold"),
                                          fg='#FF0000')
                        text_overlay.place(relx=0.5, rely=0.5, anchor="center")
                    
                    window.after(500, lambda: scare_sequence(3))
                    return
                
                // Calculate intermediate size with overshoot
                t = frame / 30
                t = t * t * (3 - 2 * t)  // Smooth step
                
                // Add slight overshoot
                if frame > 20:
                    overshoot = math.sin((frame-20) * 0.5) * 0.1
                    t = min(1.0, t + overshoot)
                
                current_width = int(start_width + (target_width - start_width) * t)
                current_height = int(start_height + (target_height - start_height) * t)
                current_x = int(start_x + (target_x - start_x) * t)
                current_y = int(start_y + (target_y - start_y) * t)
                
                window.geometry(f"{current_width}x{current_height}+{current_x}+{current_y}")
                
                // Update image size
                if image_label:
                    image_label.place(x=0, y=0, width=current_width, height=current_height)
                
                window.after(16, lambda: demonic_expand(frame + 1))
            
            demonic_expand()
        
        // Start the scare sequence
        scare_sequence(0)
    
    def final_demonic_destroy():
        """Final demonic cleanup"""
        try:
            // Flash sequence
            colors = ['#FF0000', '#FFFFFF', '#000000', '#FF0000']
            for color in colors:
                if window.winfo_exists():
                    window.configure(bg=color)
                    window.update()
                    time.sleep(0.08)
            
            // Clean up
            for canvas in active_canvases[:]:
                try:
                    if canvas.winfo_exists():
                        canvas.destroy()
                except:
                    pass
            
            if window.winfo_exists():
                window.destroy()
                
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] 12-second TERRIFYING scare completed!")
                
        except Exception as e:
            print(f"[ERROR] Final destroy error: {e}")
    
    // Schedule terrifying scare after 12 seconds TOTAL
    window.after(11500, terrifying_final_scare)
    
    // Print to console
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] TERRIFYING WINDOW ACTIVATED - 12 SECOND VERSION")
    print(f"[{current_time}] [WARNING] This may be extremely disturbing!")
    
    // Bind escape key to close window
    def on_escape(event):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Escape pressed, closing window")
        final_demonic_destroy()
    
    window.bind('<Escape>', on_escape)
    
    // Run the window
    try:
        window.mainloop()
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Window error: {e}")
    
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] Window deactivated")

if __name__ == "__main__":
    try:
        // Try to import required modules
        try:
            from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps, ImageDraw
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Installing Pillow...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--quiet"])
            from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps, ImageDraw
        
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
