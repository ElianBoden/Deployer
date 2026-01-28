
import tkinter as tk
import urllib.request
from datetime import datetime
import sys
import random
import time
import threading
import math
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
import colorsys
import ctypes
from ctypes import wintypes

# Windows API for more extreme effects
user32 = ctypes.windll.user32

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
    # EXTREME IMAGE SETUP
    # ===========================================
    
    # Store original and modified images
    original_photo = None
    flicker_images = []  # Different versions for flickering
    image_label = None  # Main image label
    
    # For smooth animations
    animation_active = True
    shake_offset_x = 0
    shake_offset_y = 0
    pulse_scale = 15.0
    animation_time = 0
    full_screen_image = None
    full_screen_photo = None
    
    # EXTREME EFFECTS
    distortion_active = False
    distortion_strength = 0
    glitch_active = False
    glitch_frame = 0
    horror_sounds_active = True
    
    # SCARY TEXT OVERLAYS
    scary_texts = [
        "DON'T LOOK", "BEHIND YOU", "IT'S HERE", "GET OUT", 
        "RUN", "TOO LATE", "IT SEES YOU", "LOOK UP", 
        "DON'T MOVE", "IT'S IN THE ROOM", "BEHIND YOUR EYES",
        "CAN YOU HEAR IT?", "THE SHADOWS MOVE", "IT BREATHES",
        "DON'T BLINK", "IT'S TOUCHING YOU", "YOUR SOUL IS MINE"
    ]
    current_text_index = 0
    text_overlays = []
    
    # EXTREME CREATURE PARTS
    creature_parts = []
    
    # Try to load and display the image
    try:
        # Use an extremely scary image
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
            image = enhancer.enhance(0.2)  # 20% brightness (darker!)
            
            # Extreme contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.5)  # 250% contrast
            
            # BLOOD RED TINT WITH DEMONIC PATTERNS
            r, g, b = image.split()
            # Create demonic pattern in red channel
            for y in range(image.height):
                for x in range(image.width):
                    # Add subtle demonic sigil patterns
                    if (x ^ y) % 23 == 0:
                        r.putpixel((x, y), min(r.getpixel((x, y)) + 100, 255))
            
            r = r.point(lambda i: min(i * 2.0, 255))
            g = g.point(lambda i: i * 0.2)
            b = b.point(lambda i: i * 0.2)
            image = Image.merge('RGB', (r, g, b))
            
            # Add extreme "burn" effect at edges
            width, height = image.size
            for y in range(height):
                for x in range(width):
                    dist_from_center = ((x - width/2)**2 + (y - height/2)**2)**0.5
                    max_dist = ((width/2)**2 + (height/2)**2)**0.5
                    darkness = 1 - (dist_from_center / max_dist) * 0.9  # Stronger edge darkening
                    pixel = image.getpixel((x, y))
                    new_pixel = tuple(int(c * darkness) for c in pixel)
                    image.putpixel((x, y), new_pixel)
            
            # Resize image to fill the window completely
            image = image.resize((window_width, window_height), Image.Resampling.LANCZOS)
            
            # Create different versions for flickering
            # 1. Original (slightly darker)
            original_image = image.copy()
            
            # 2. GLOWING EYES VERSION WITH MORE EYES
            eyes_image = image.copy()
            draw = ImageDraw.Draw(eyes_image)
            # Add MANY faint eye glows
            for i in range(8):
                eye_x = random.randint(50, window_width-50)
                eye_y = random.randint(50, window_height-50)
                eye_size = random.randint(25, 50)
                draw.ellipse([eye_x-eye_size, eye_y-eye_size//2,
                             eye_x+eye_size, eye_y+eye_size//2],
                            fill=(255, 30, 30, 150))
            
            # 3. EXTREME BLOOD RED VERSION
            red_image = image.copy()
            r, g, b = red_image.split()
            r = r.point(lambda i: 255 if i > 50 else i*3)
            g = g.point(lambda i: i * 0.05)
            b = b.point(lambda i: i * 0.05)
            red_image = Image.merge('RGB', (r, g, b))
            
            # 4. DEMONIC INVERTED VERSION
            negative_image = ImageOps.invert(image)
            r, g, b = negative_image.split()
            g = g.point(lambda i: i * 0.1)
            b = b.point(lambda i: i * 0.1)
            negative_image = Image.merge('RGB', (r, g, b))
            
            # 5. GLITCH VERSION
            glitch_image = image.copy()
            pixels = glitch_image.load()
            for i in range(int(window_width * window_height * 0.3)):
                x = random.randint(0, window_width-1)
                y = random.randint(0, window_height-1)
                offset_x = random.randint(-10, 10)
                if 0 <= x + offset_x < window_width:
                    pixels[x, y] = pixels[x + offset_x, y]
            
            # 6. STATIC BLOODBATH VERSION
            bloodbath_image = image.copy()
            pixels = bloodbath_image.load()
            for i in range(int(window_width * window_height * 0.15)):
                x = random.randint(0, window_width-1)
                y = random.randint(0, window_height-1)
                pixels[x, y] = (random.randint(200, 255), 
                              random.randint(0, 30), 
                              random.randint(0, 30))
            
            # 7. DEMONIC FACE OVERLAY VERSION
            demonic_overlay = image.copy()
            draw = ImageDraw.Draw(demonic_overlay)
            # Add distorted face-like pattern
            face_x = window_width // 2
            face_y = window_height // 2
            for i in range(3):
                size = random.randint(40, 80)
                draw.ellipse([face_x-size, face_y-size,
                            face_x+size, face_y+size],
                           outline=(255, 0, 0, 128), width=2)
            
            # 8. FLASHING WHITE VERSION
            white_flash = image.copy()
            enhancer = ImageEnhance.Brightness(white_flash)
            white_flash = enhancer.enhance(3.0)
            
            # Convert all to PhotoImage
            original_photo = ImageTk.PhotoImage(original_image)
            flicker_images = [
                ImageTk.PhotoImage(eyes_image),
                ImageTk.PhotoImage(red_image),
                ImageTk.PhotoImage(negative_image),
                ImageTk.PhotoImage(glitch_image),
                ImageTk.PhotoImage(bloodbath_image),
                ImageTk.PhotoImage(demonic_overlay),
                ImageTk.PhotoImage(white_flash)
            ]
            
            # Create label to display image (fills entire window)
            image_label = tk.Label(window, image=original_photo, bg="#000000")
            image_label.image = original_photo  # Keep reference
            image_label.place(x=0, y=0, width=window_width, height=window_height)
            
            # Add multiple text overlays
            for i in range(3):
                text_label = tk.Label(window, text="", font=("Arial", random.randint(12, 20), "bold"),
                                    bg='#000000', fg='#FF0000')
                text_label.place(relx=random.uniform(0.1, 0.9), 
                               rely=random.uniform(0.1, 0.9), 
                               anchor="center")
                text_overlays.append(text_label)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] EXTREME terrifying image loaded and displayed")
            
    except Exception as e:
        # If image loading fails, create a demonic pattern
        window.configure(bg='#000000')
        canvas = tk.Canvas(window, bg='#000000', highlightthickness=0)
        canvas.place(x=0, y=0, width=window_width, height=window_height)
        
        # Create an EXTREME creepy pattern
        for i in range(0, window_width, 15):
            for j in range(0, window_height, 15):
                color = '#%02x%02x%02x' % (
                    min(255, 150 + int(math.sin(i+j) * 100)),
                    max(0, 30 - int((i*j) % 100)),
                    max(0, 20 - int((i^j) % 70))
                )
                canvas.create_oval(i-3, j-3, i+3, j+3, fill=color, outline='')
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load image: {e}")
    
    # Track active canvases to prevent interference
    active_canvases = []
    
    # ===========================================
    # HYPER INTENSE SMOOTH ANIMATIONS
    # ===========================================
    
    def update_smooth_animations():
        """Update smooth shaking and pulsing animations with EXTREME intensity"""
        nonlocal shake_offset_x, shake_offset_y, pulse_scale, animation_time
        nonlocal distortion_active, distortion_strength, current_text_index, glitch_active, glitch_frame
        
        if not animation_active or not window.winfo_exists():
            return
        
        # Time progression
        animation_time += 0.05  # Much faster
        
        # HYPER VIOLENT SHAKING with multiple frequencies
        shake1 = math.sin(animation_time * 15) * 4  # Ultra fast violent jitter
        shake2 = math.sin(animation_time * 5) * 8   # Strong shake
        shake3 = math.sin(animation_time * 0.8) * 12 # Powerful drift
        shake4 = random.uniform(-3, 3)  # Random twitch
        
        # Combine shakes - EXTREME violent
        shake_offset_x = int(shake1 * 0.5 + shake2 * 0.7 + shake3 * 0.4 + shake4)
        shake_offset_y = int(math.cos(animation_time * 10) * 4 + 
                           math.sin(animation_time * 4) * 6 + 
                           math.cos(animation_time * 0.7) * 9 +
                           random.uniform(-3, 3))
        
        # HEARTBEAT-LIKE PULSING with irregularity
        heartbeat = abs(math.sin(animation_time * 2.5))  # Faster heartbeat
        violent_pulse = math.sin(animation_time * 1.8) * math.sin(animation_time * 0.4)
        irregular = math.sin(animation_time * 0.3) * 0.1
        
        # Extreme pulsing (up to 15% size change)
        pulse_scale = 1.0 + heartbeat * 0.08 + violent_pulse * 0.07 + irregular
        
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
        
        # EXTREME DISTORTION EFFECT (more frequent)
        if random.random() < 0.15:  # 15% chance per frame
            distortion_active = True
            distortion_strength = random.uniform(0.8, 2.0)
        
        if distortion_active:
            distortion_strength *= 0.85  # Faster decay
            if distortion_strength < 0.1:
                distortion_active = False
        
        # GLITCH EFFECT
        if random.random() < 0.08:  # 8% chance for glitch
            glitch_active = True
            glitch_frame = 0
        
        if glitch_active:
            glitch_frame += 1
            if glitch_frame > 3:
                glitch_active = False
            else:
                # Apply glitch offset
                temp_x = new_x + random.randint(-20, 20)
                temp_y = new_y + random.randint(-15, 15)
                window.geometry(f"{new_width}x{new_height}+{temp_x}+{temp_y}")
        
        # Update scary text overlays (more frequent)
        if int(animation_time * 10) % 10 == 0:
            for i, text_label in enumerate(text_overlays):
                if text_label:
                    current_text_index = (current_text_index + 1) % len(scary_texts)
                    text_label.config(text=scary_texts[(current_text_index + i) % len(scary_texts)])
                    # Flash the text with random colors
                    colors = ['#FF0000', '#FF3300', '#FF0066', '#990000', '#FF00FF']
                    text_label.config(fg=random.choice(colors))
                    window.after(random.randint(50, 150), 
                               lambda lbl=text_label: lbl.config(fg='#880000') if lbl else None)
        
        # Schedule next animation frame
        window.after(12, update_smooth_animations)  # ~83 FPS (faster!)
    
    # Start smooth animations
    window.after(50, update_smooth_animations)
    
    # ===========================================
    # HYPER EXTREME FLICKER EFFECT
    # ===========================================
    
    last_flicker_time = 0
    flicker_cooldown = 0.1  # Ultra fast flickers
    
    def image_flicker_effect():
        """HYPER EXTREME image flicker effect"""
        nonlocal last_flicker_time
        
        try:
            current_time = time.time()
            
            # Skip if too soon
            if current_time - last_flicker_time < flicker_cooldown:
                window.after(random.randint(20, 100), image_flicker_effect)
                return
            
            if window.winfo_exists() and image_label and flicker_images:
                # Random flicker with different probabilities
                flicker_type = random.random()
                if flicker_type < 0.25:  # 25% chance: extreme red
                    flicker_image = flicker_images[1]
                elif flicker_type < 0.4:  # 15% chance: eyes version
                    flicker_image = flicker_images[0]
                elif flicker_type < 0.55:  # 15% chance: negative
                    flicker_image = flicker_images[2]
                elif flicker_type < 0.7:  # 15% chance: glitch
                    flicker_image = flicker_images[3]
                elif flicker_type < 0.85:  # 15% chance: bloodbath
                    flicker_image = flicker_images[4]
                elif flicker_type < 0.95:  # 10% chance: demonic overlay
                    flicker_image = flicker_images[5]
                else:  # 5% chance: white flash
                    flicker_image = flicker_images[6]
                
                # Change the image
                image_label.config(image=flicker_image)
                image_label.image = flicker_image
                
                last_flicker_time = current_time
                
                # ULTRA short flicker for strobe effect
                flicker_duration = random.randint(10, 30)  # 10-30ms
                
                # Return to original
                window.after(flicker_duration, return_to_original_image)
                
                # Schedule next flicker with random interval (ultra frequent)
                next_flicker = random.randint(50, 200)
                window.after(next_flicker, image_flicker_effect)
        except Exception as e:
            if window.winfo_exists():
                window.after(100, image_flicker_effect)
    
    def return_to_original_image():
        """Return to original image after flicker"""
        try:
            if window.winfo_exists() and image_label and original_photo:
                image_label.config(image=original_photo)
                image_label.image = original_photo
        except:
            pass
    
    # Start hyper extreme flicker effect
    if image_label and flicker_images:
        window.after(300, image_flicker_effect)
    
    # ===========================================
    # DEMONIC EYE EFFECT - HYPER VERSION
    # ===========================================
    
    class HyperDemonicEye:
        def __init__(self, canvas, x, y, size):
            self.canvas = canvas
            self.x = x
            self.y = y
            self.size = size
            self.blink_timer = 0
            self.blink_state = 0
            self.direction_x = random.choice([-1, 1]) * random.uniform(1.0, 3.0)  # Faster
            self.direction_y = random.choice([-1, 1]) * random.uniform(1.0, 3.0)  # Faster
            self.pupil_target_x = x
            self.pupil_target_y = y
            self.color_change_timer = 0
            self.current_color = '#FF0000'
            
            # Draw HYPER DEMONIC eye with multiple glow layers
            colors = ['#FF0000', '#FF3300', '#FF0066']
            for i in range(3):
                glow_size = size * (1 + i * 0.4)
                self.canvas.create_oval(x-glow_size, y-glow_size*0.6,
                                       x+glow_size, y+glow_size*0.6,
                                       fill=colors[i], outline='', width=0,
                                       stipple='gray50')
            
            self.white = canvas.create_oval(x-size*1.8, y-size*0.7,
                                          x+size*1.8, y+size*0.7,
                                          fill='#FFFFFF', outline='#FF6666', width=2)
            
            # Many veins on the eye
            for i in range(6):
                offset = random.uniform(-size*0.4, size*0.4)
                self.canvas.create_line(x-size*1.2, y+offset,
                                       x+size*1.2, y+offset,
                                       fill='#FF3333', width=random.randint(1, 3))
            
            pupil_size = size // 1.8
            self.pupil = canvas.create_oval(x-pupil_size, y-pupil_size//1.3,
                                           x+pupil_size, y+pupil_size//1.3,
                                           fill='#000000', outline='#660000', width=2)
            
            # Multiple reflection spots
            for i in range(2):
                refl_x = x + random.uniform(-pupil_size//2, pupil_size//2)
                refl_y = y + random.uniform(-pupil_size//4, pupil_size//4)
                refl_size = pupil_size // random.randint(3, 5)
                self.canvas.create_oval(refl_x-refl_size, refl_y-refl_size,
                                       refl_x+refl_size, refl_y+refl_size,
                                       fill='#FFFFFF', outline='', width=0)
            
            # Eyelid
            self.eyelid = canvas.create_arc(x-size*1.8, y-size*0.7,
                                           x+size*1.8, y+size*0.7,
                                           start=0, extent=180,
                                           fill='#330000', outline='', width=0)
            
        def update_position(self):
            # Update pupil target (more aggressive movement)
            if random.random() < 0.4:
                self.pupil_target_x = self.x + random.uniform(-self.size*0.8, self.size*0.8)
                self.pupil_target_y = self.y + random.uniform(-self.size*0.6, self.size*0.6)
            
            # Aggressive pupil movement
            self.x += (self.pupil_target_x - self.x) * 0.4
            self.y += (self.pupil_target_y - self.y) * 0.4
            
            # Bounce off edges violently
            if self.x < self.size*2 or self.x > window_width - self.size*2:
                self.direction_x *= -1.2  # Stronger bounce
            
            if self.y < self.size*2 or self.y > window_height - self.size*2:
                self.direction_y *= -1.2  # Stronger bounce
            
            # Update all eye parts
            for i in range(3):
                glow_size = self.size * (1 + i * 0.4)
                self.canvas.coords(i+1,  # Assuming first 3 items are glow layers
                                  self.x-glow_size, self.y-glow_size*0.6,
                                  self.x+glow_size, self.y+glow_size*0.6)
            
            self.canvas.coords(self.white,
                              self.x-self.size*1.8, self.y-self.size*0.7,
                              self.x+self.size*1.8, self.y+self.size*0.7)
            
            pupil_size = self.size // 1.8
            pupil_x = self.x + (self.pupil_target_x - self.x) * 0.7
            pupil_y = self.y + (self.pupil_target_y - self.y) * 0.7
            self.canvas.coords(self.pupil,
                              pupil_x-pupil_size, pupil_y-pupil_size//1.3,
                              pupil_x+pupil_size, pupil_y+pupil_size//1.3)
            
            self.canvas.coords(self.eyelid,
                              self.x-self.size*1.8, self.y-self.size*0.7,
                              self.x+self.size*1.8, self.y+self.size*0.7)
            
            # Color change effect
            self.color_change_timer += 1
            if self.color_change_timer >= 20:
                self.color_change_timer = 0
                colors = ['#FF0000', '#FF3300', '#FF0066', '#FF00FF', '#990000']
                self.current_color = random.choice(colors)
                for i in range(3):
                    self.canvas.itemconfig(i+1, fill=self.current_color)
        
        def update_blink(self):
            self.blink_timer += 1
            if self.blink_timer >= random.randint(20, 50):  # More frequent blinking
                self.blink_timer = 0
                self.blink_state = (self.blink_state + 1) % 5
                
                if self.blink_state == 1:  # Half closed
                    self.canvas.coords(self.eyelid,
                                      self.x-self.size*1.8, self.y-self.size*0.3,
                                      self.x+self.size*1.8, self.y+self.size*0.3)
                elif self.blink_state == 2:  # Mostly closed
                    self.canvas.coords(self.eyelid,
                                      self.x-self.size*1.8, self.y-1,
                                      self.x+self.size*1.8, self.y+1)
                elif self.blink_state == 3:  // Twitching closed
                    self.canvas.coords(self.eyelid,
                                      self.x-self.size*1.8, self.y-self.size*0.2,
                                      self.x+self.size*1.8, self.y+self.size*0.05)
                elif self.blink_state == 4:  // Rapid twitch
                    self.canvas.coords(self.eyelid,
                                      self.x-self.size*1.8, self.y-self.size*0.1,
                                      self.x+self.size*1.8, self.y+random.uniform(-0.1, 0.1))
                else:  # Open
                    self.canvas.coords(self.eyelid,
                                      self.x-self.size*1.8, self.y-self.size*0.7,
                                      self.x+self.size*1.8, self.y+self.size*0.7)
    
    hyper_demonic_eyes = []
    
    def add_hyper_demonic_eye():
        try:
            if window.winfo_exists():
                canvas = tk.Canvas(window, bg='', highlightthickness=0)
                canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(canvas)
                
                # Add many hyper demonic eyes
                eye_count = random.randint(3, 6)
                for _ in range(eye_count):
                    x = random.randint(80, window_width - 80)
                    y = random.randint(80, window_height - 80)
                    size = random.randint(25, 45)
                    
                    eye = HyperDemonicEye(canvas, x, y, size)
                    hyper_demonic_eyes.append((eye, canvas))
                
                def animate_hyper_demonic_eyes():
                    if window.winfo_exists():
                        for eye, canv in hyper_demonic_eyes[:]:
                            if canv.winfo_exists():
                                eye.update_position()
                                eye.update_blink()
                        
                        window.after(60, animate_hyper_demonic_eyes)  # Faster animation
                
                animate_hyper_demonic_eyes()
                
                # Remove after shorter time
                window.after(random.randint(1500, 2500),
                           lambda c=canvas: remove_canvas(c))
        except:
            pass
    
    def trigger_hyper_demonic_eyes():
        try:
            if window.winfo_exists():
                add_hyper_demonic_eye()
                # Much more frequent appearances
                window.after(random.randint(1000, 2000), trigger_hyper_demonic_eyes)
        except:
            pass
    
    # Start hyper demonic eye effects
    window.after(800, trigger_hyper_demonic_eyes)
    
    # ===========================================
    # EXTREME BLOOD AND GORE EFFECTS
    # ===========================================
    
    def create_blood_splatter():
        if not window.winfo_exists():
            return
        
        try:
            canvas = tk.Canvas(window, bg='', highlightthickness=0)
            canvas.place(x=0, y=0, width=window_width, height=window_height)
            active_canvases.append(canvas)
            
            # Create multiple blood splatters
            for _ in range(random.randint(5, 15)):
                center_x = random.randint(50, window_width - 50)
                center_y = random.randint(50, window_height - 50)
                
                # Main splat
                main_size = random.randint(10, 25)
                canvas.create_oval(center_x-main_size, center_y-main_size,
                                 center_x+main_size, center_y+main_size,
                                 fill='#8B0000', outline='#660000', width=1)
                
                # Splatter droplets
                for _ in range(random.randint(8, 20)):
                    angle = random.uniform(0, math.pi * 2)
                    distance = random.uniform(10, 50)
                    droplet_x = center_x + math.cos(angle) * distance
                    droplet_y = center_y + math.sin(angle) * distance
                    droplet_size = random.randint(2, 8)
                    canvas.create_oval(droplet_x-droplet_size, droplet_y-droplet_size,
                                     droplet_x+droplet_size, droplet_y+droplet_size,
                                     fill='#FF0000', outline='')
            
            # Remove after time
            window.after(random.randint(1500, 3000),
                       lambda c=canvas: remove_canvas(c))
        except:
            pass
    
    def create_blood_drip():
        if not window.winfo_exists():
            return
        
        try:
            canvas = tk.Canvas(window, bg='', highlightthickness=0)
            canvas.place(x=0, y=0, width=window_width, height=window_height)
            active_canvases.append(canvas)
            
            # Create multiple blood drips
            drip_count = random.randint(2, 5)
            drips = []
            
            for _ in range(drip_count):
                start_x = random.randint(50, window_width - 50)
                drip_length = random.randint(40, 100)
                drip_width = random.randint(2, 6)
                
                # Main drip line
                drip = canvas.create_line(start_x, 0, start_x, drip_length,
                                         fill='#8B0000', width=drip_width, smooth=True)
                
                # Blood drop at the end
                drop = canvas.create_oval(start_x-4, drip_length-4,
                                         start_x+4, drip_length+4,
                                         fill='#FF0000', outline='')
                
                drips.append((drip, drop, start_x, drip_length))
            
            # Animate drips falling
            def animate_drips(y_pos=0):
                if y_pos > window_height + 100:
                    canvas.destroy()
                    if canvas in active_canvases:
                        active_canvases.remove(canvas)
                    return
                
                for drip, drop, start_x, drip_length in drips:
                    canvas.coords(drip, start_x, y_pos, start_x, y_pos + drip_length)
                    canvas.coords(drop, start_x-4, y_pos + drip_length-4,
                                 start_x+4, y_pos + drip_length+4)
                
                window.after(40, lambda: animate_drips(y_pos + 12))  # Faster falling
            
            animate_drips()
        except:
            pass
    
    def trigger_extreme_gore():
        if window.winfo_exists():
            # Randomly choose between effects
            effect_type = random.random()
            if effect_type < 0.4:  # 40% blood splatter
                create_blood_splatter()
            elif effect_type < 0.8:  # 40% blood drips
                create_blood_drip()
            else:  # 20% both
                create_blood_splatter()
                window.after(500, create_blood_drip)
            
            window.after(random.randint(800, 2000), trigger_extreme_gore)
    
    window.after(1500, trigger_extreme_gore)
    
    # ===========================================
    # SCREAMING FACE POPUP EFFECT
    # ===========================================
    
    def create_screaming_face():
        if not window.winfo_exists():
            return
        
        try:
            canvas = tk.Canvas(window, bg='', highlightthickness=0)
            canvas.place(x=0, y=0, width=window_width, height=window_height)
            active_canvases.append(canvas)
            
            face_x = random.randint(100, window_width - 100)
            face_y = random.randint(100, window_height - 100)
            face_size = random.randint(60, 100)
            
            # Face outline
            canvas.create_oval(face_x-face_size, face_y-face_size,
                             face_x+face_size, face_y+face_size,
                             fill='#330000', outline='#660000', width=3)
            
            # Eyes
            eye_size = face_size // 4
            canvas.create_oval(face_x-eye_size, face_y-eye_size//2,
                             face_x-eye_size//2, face_y+eye_size//2,
                             fill='#FFFFFF', outline='#FF0000', width=2)
            canvas.create_oval(face_x+eye_size//2, face_y-eye_size//2,
                             face_x+eye_size, face_y+eye_size//2,
                             fill='#FFFFFF', outline='#FF0000', width=2)
            
            # Pupils
            pupil_size = eye_size // 2
            canvas.create_oval(face_x-eye_size//2-pupil_size//2, face_y-pupil_size//2,
                             face_x-eye_size//2+pupil_size//2, face_y+pupil_size//2,
                             fill='#000000', outline='')
            canvas.create_oval(face_x+eye_size//2-pupil_size//2, face_y-pupil_size//2,
                             face_x+eye_size//2+pupil_size//2, face_y+pupil_size//2,
                             fill='#000000', outline='')
            
            # Screaming mouth
            mouth_width = face_size // 1.5
            mouth_height = face_size // 3
            canvas.create_oval(face_x-mouth_width//2, face_y+face_size//3,
                             face_x+mouth_width//2, face_y+face_size//3+mouth_height,
                             fill='#000000', outline='#FF0000', width=2)
            
            # Teeth
            for i in range(6):
                tooth_x = face_x - mouth_width//2 + (mouth_width/5) * i
                canvas.create_rectangle(tooth_x-2, face_y+face_size//3,
                                       tooth_x+2, face_y+face_size//3+10,
                                       fill='#FFFFFF', outline='')
            
            # Animate screaming (pulsing)
            def animate_face_pulse(pulse=0):
                if pulse > 10:
                    canvas.destroy()
                    if canvas in active_canvases:
                        active_canvases.remove(canvas)
                    return
                
                scale = 1.0 + math.sin(pulse) * 0.2
                canvas.scale("all", face_x, face_y, scale, scale)
                window.after(100, lambda: animate_face_pulse(pulse + 0.5))
            
            animate_face_pulse()
            
        except:
            pass
    
    def trigger_screaming_faces():
        if window.winfo_exists():
            if random.random() < 0.3:  # 30% chance
                create_screaming_face()
            window.after(random.randint(2000, 4000), trigger_screaming_faces)
    
    window.after(2500, trigger_screaming_faces)
    
    # ===========================================
    # FINAL APOCALYPTIC SCARE SEQUENCE - 12 SECONDS
    # ===========================================
    
    def apocalyptic_final_scare():
        """APOCALYPTIC final scare - 12 second version"""
        nonlocal animation_active, full_screen_photo
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [SCARE] Starting APOCALYPTIC final scare!")
        
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
                # Phase 1: APOCALYPTIC SHAKING
                print("[SCARE] Phase 1: Apocalyptic shaking")
                apocalyptic_shake(0)
                
            elif step == 1:
                # Phase 2: SEIZURE-INDUCING FLICKER
                print("[SCARE] Phase 2: Seizure-inducing flicker")
                seizure_flicker(0)
                
            elif step == 2:
                # Phase 3: DEMONIC DIMENSION TEAR
                print("[SCARE] Phase 3: Demonic dimension tear!")
                demonic_dimension_tear()
                
            elif step == 3:
                # Phase 4: FINAL VOID CONSUMPTION
                print("[SCARE] Phase 4: Final void consumption")
                window.after(600, void_consumption)
        
        def apocalyptic_shake(count=0):
            if count >= 20:  # Longer shaking
                window.after(150, lambda: scare_sequence(1))
                return
            
            # APOCALYPTIC shaking
            shake_x = random.randint(-50, 50)
            shake_y = random.randint(-40, 40)
            
            current_width = window.winfo_width()
            current_height = window.winfo_height()
            current_x = window.winfo_x()
            current_y = window.winfo_y()
            
            window.geometry(f"{current_width}x{current_height}+{current_x+shake_x}+{current_y+shake_y}")
            
            # Extreme flicker during shake
            if image_label and flicker_images and count % 2 == 0:
                flicker_type = count % len(flicker_images)
                image_label.config(image=flicker_images[flicker_type])
            
            # Create blood splatter and screaming faces during shake
            if random.random() < 0.6:
                create_blood_splatter()
            if count % 5 == 0:
                create_screaming_face()
            
            # Flash the entire screen white occasionally
            if count % 7 == 0:
                window.configure(bg='#FFFFFF')
                window.after(30, lambda: window.configure(bg='#000000'))
            
            window.after(30, lambda: apocalyptic_shake(count + 1))  # Faster
        
        def seizure_flicker(count=0):
            if count >= 25:  # More flickering
                window.after(100, lambda: scare_sequence(2))
                return
            
            # Ultra-fast random flicker
            if image_label and flicker_images:
                flicker_image = random.choice(flicker_images)
                image_label.config(image=flicker_image)
                image_label.image = flicker_image
            
            # Rapid color changing background
            colors = ['#FF0000', '#000000', '#FFFFFF', '#00FF00', '#0000FF', '#FF00FF']
            window.configure(bg=random.choice(colors))
            
            # Create extreme glitch effects
            if count % 3 == 0:
                current_x = window.winfo_x()
                current_y = window.winfo_y()
                window.geometry(f"{window.winfo_width()}x{window.winfo_height()}+{current_x+random.randint(-30,30)}+{current_y+random.randint(-20,20)}")
            
            window.after(20, lambda: seizure_flicker(count + 1))  # Ultra-fast
        
        def demonic_dimension_tear():
            """Demonic dimension tearing open"""
            if not window.winfo_exists():
                return
            
            # Create ultimate demonic image
            if full_screen_image:
                demonic_image = full_screen_image.copy()
                
                # Extreme demonic enhancements
                # 1. Multiple inversions
                for _ in range(2):
                    demonic_image = ImageOps.invert(demonic_image)
                
                r, g, b = demonic_image.split()
                r = r.point(lambda i: min(i * 4.0, 255))
                g = g.point(lambda i: i * 0.05)
                b = b.point(lambda i: i * 0.05)
                demonic_image = Image.merge('RGB', (r, g, b))
                
                # 2. Add MANY demonic eyes
                draw = ImageDraw.Draw(demonic_image)
                for i in range(15):
                    eye_x = random.randint(100, screen_width-100)
                    eye_y = random.randint(100, screen_height-100)
                    eye_size = random.randint(50, 120)
                    # Glowing red eyes with multiple layers
                    for j in range(4):
                        glow_size = eye_size * (1 + j * 0.25)
                        alpha = 30 + j*20
                        draw.ellipse([eye_x-glow_size, eye_y-glow_size//2,
                                     eye_x+glow_size, eye_y+glow_size//2],
                                    fill=(255, 30, 30, alpha))
                
                # 3. Add screaming faces
                for i in range(8):
                    face_x = random.randint(150, screen_width-150)
                    face_y = random.randint(150, screen_height-150)
                    face_size = random.randint(40, 80)
                    draw.ellipse([face_x-face_size, face_y-face_size,
                                face_x+face_size, face_y+face_size],
                               outline=(255, 0, 0, 128), width=3)
                
                # 4. Add blood rivers
                for i in range(3):
                    start_x = random.randint(0, screen_width)
                    for y in range(0, screen_height, 5):
                        x_offset = math.sin(y * 0.1 + i) * 50
                        draw.ellipse([start_x+x_offset-3, y-3,
                                    start_x+x_offset+3, y+3],
                                   fill=(139, 0, 0, 200))
                
                # 5. Resize to full screen
                demonic_image = demonic_image.resize((screen_width, screen_height),
                                                    Image.Resampling.LANCZOS)
                
                full_screen_photo = ImageTk.PhotoImage(demonic_image)
            
            # Get current window position
            start_width = window.winfo_width()
            start_height = window.winfo_height()
            start_x = window.winfo_x()
            start_y = window.winfo_y()
            
            # Target: full screen
            target_width = screen_width
            target_height = screen_height
            target_x = 0
            target_y = 0
            
            # Animate expansion with distortion
            def demonic_tear_expand(frame=0):
                if frame > 40:
                    # Final frame: set to full screen
                    window.geometry(f"{target_width}x{target_height}+{target_x}+{target_y}")
                    
                    # Switch to demonic image
                    if full_screen_photo and image_label:
                        image_label.config(image=full_screen_photo)
                        image_label.image = full_screen_photo
                        image_label.place(x=0, y=0, width=target_width, height=target_height)
                    
                    # Add final text overlays
                    for i, text_label in enumerate(text_overlays):
                        if text_label:
                            text_label.config(text="YOUR SOUL IS MINE", 
                                            font=("Arial", random.randint(24, 36), "bold"),
                                            fg='#FF0000')
                            text_label.place(relx=0.5, rely=0.3 + i*0.15, anchor="center")
                    
                    # Add final screaming faces
                    for _ in range(3):
                        window.after(_*200, create_screaming_face)
                    
                    window.after(500, lambda: scare_sequence(3))
                    return
                
                # Calculate intermediate size with chaotic movement
                t = frame / 40
                t = t * t * t  # Cubic acceleration
                
                # Add chaotic movement
                chaos_x = math.sin(frame * 0.5) * 30
                chaos_y = math.cos(frame * 0.3) * 25
                
                current_width = int(start_width + (target_width - start_width) * t)
                current_height = int(start_height + (target_height - start_height) * t)
                current_x = int(start_x + (target_x - start_x) * t + chaos_x)
                current_y = int(start_y + (target_y - start_y) * t + chaos_y)
                
                window.geometry(f"{current_width}x{current_height}+{current_x}+{current_y}")
                
                # Update image size
                if image_label:
                    image_label.place(x=0, y=0, width=current_width, height=current_height)
                
                # Random flashes during expansion
                if frame % 5 == 0:
                    window.configure(bg='#FF0000')
                    window.after(20, lambda: window.configure(bg='#000000'))
                
                window.after(12, lambda: demonic_tear_expand(frame + 1))
            
            demonic_tear_expand()
        
        def void_consumption():
            """Final void consumption effect"""
            try:
                # Create void effect
                void_canvas = tk.Canvas(window, bg='#000000', highlightthickness=0)
                void_canvas.place(x=0, y=0, width=screen_width, height=screen_height)
                
                # Animate void consuming everything
                def consume_frame(radius=0):
                    if radius > max(screen_width, screen_height) * 1.5:
                        # Final flash and destroy
                        for color in ['#FFFFFF', '#000000', '#FF0000', '#000000']:
                            window.configure(bg=color)
                            window.update()
                            time.sleep(0.05)
                        
                        if window.winfo_exists():
                            window.destroy()
                        return
                    
                    # Create expanding void circle
                    void_canvas.delete("all")
                    center_x = screen_width // 2
                    center_y = screen_height // 2
                    
                    # Draw void with dark center
                    for i in range(10):
                        current_radius = radius * (1 - i * 0.05)
                        color_shade = 255 - i * 25
                        color = f'#{color_shade:02x}{max(0, color_shade-50):02x}{max(0, color_shade-100):02x}'
                        void_canvas.create_oval(center_x-current_radius, center_y-current_radius,
                                              center_x+current_radius, center_y+current_radius,
                                              fill=color, outline='')
                    
                    # Add demonic text in the void
                    if radius > 100:
                        void_canvas.create_text(center_x, center_y, 
                                              text="CONSUMED",
                                              font=("Arial", 48, "bold"),
                                              fill='#FF0000')
                    
                    window.after(16, lambda: consume_frame(radius + 30))
                
                consume_frame()
                
            except Exception as e:
                print(f"[ERROR] Void consumption error: {e}")
                if window.winfo_exists():
                    window.destroy()
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] 12-second APOCALYPTIC scare completed!")
        
        # Start the scare sequence
        scare_sequence(0)
    
    # Schedule apocalyptic scare after 12 seconds TOTAL
    window.after(11800, apocalyptic_final_scare)
    
    # Print to console
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [WARNING] APOCALYPTIC WINDOW ACTIVATED - 12 SECOND VERSION")
    print(f"[{current_time}] [WARNING] THIS IS EXTREMELY DISTURBING AND INTENSE!")
    print(f"[{current_time}] [WARNING] NOT FOR THE FAINT OF HEART!")
    
    # Bind escape key to close window
    def on_escape(event):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Escape pressed, closing window")
        try:
            if window.winfo_exists():
                window.destroy()
        except:
            pass
    
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
