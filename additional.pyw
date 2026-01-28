
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
    
    # Performance tracking
    frame_count = 0
    last_fps_time = time.time()
    
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
            
            # Create high-res version for full screen scare
            full_screen_image = image.copy()
            
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
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Scary image loaded and displayed")
            
    except Exception as e:
        # If image loading fails, just create a solid red screen
        window.configure(bg='#8B0000')  # Dark red
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load image, using solid color: {e}")
    
    # Track active canvases to prevent interference
    active_canvases = []
    
    # ===========================================
    # SMOOTH SHAKING AND PULSING ANIMATIONS
    # ===========================================
    
    def update_smooth_animations():
        """Update smooth shaking and pulsing animations (low CPU usage)"""
        nonlocal shake_offset_x, shake_offset_y, pulse_scale, animation_time, frame_count
        
        if not animation_active or not window.winfo_exists():
            return
        
        frame_count += 1
        current_time = time.time()
        
        # Calculate FPS (for debugging)
        if current_time - last_fps_time >= 5:
            fps = frame_count / (current_time - last_fps_time)
            if fps < 30:
                print(f"[PERF] FPS: {fps:.1f} (low)")
            frame_count = 0
        
        # Smooth shaking with multiple frequencies for more organic feel
        animation_time += 0.03  # Slow time progression
        
        # Multi-frequency shaking for more organic movement
        shake1 = math.sin(animation_time * 8) * 2  # Fast jitter
        shake2 = math.sin(animation_time * 3) * 4  # Medium shake
        shake3 = math.sin(animation_time * 0.5) * 6  # Slow drift
        
        # Combine shakes with different weights
        shake_offset_x = int(shake1 * 0.3 + shake2 * 0.5 + shake3 * 0.2)
        shake_offset_y = int(math.cos(animation_time * 7) * 2 + 
                           math.sin(animation_time * 2.5) * 3 + 
                           math.cos(animation_time * 0.4) * 4)
        
        # Gentle pulsing effect (breathing)
        pulse_speed = 0.8  # Slower pulse
        pulse_magnitude = 0.03  # 3% size change
        
        # Add heartbeat-like pulse
        pulse_scale = 1.0 + math.sin(animation_time * pulse_speed) * pulse_magnitude
        
        # Calculate new window size with pulse
        new_width = int(original_geometry['width'] * pulse_scale)
        new_height = int(original_geometry['height'] * pulse_scale)
        
        # Calculate new position (centered with shake offset)
        new_x = original_geometry['x'] + shake_offset_x - (new_width - original_geometry['width']) // 2
        new_y = original_geometry['y'] + shake_offset_y - (new_height - original_geometry['height']) // 2
        
        # Apply smooth geometry update
        window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
        
        # Update image size if it exists
        if image_label and image_label.winfo_exists():
            image_label.place(x=0, y=0, width=new_width, height=new_height)
        
        # Schedule next animation frame (target 30-60 FPS)
        window.after(20, update_smooth_animations)  # ~50 FPS
    
    # Start smooth animations
    window.after(100, update_smooth_animations)
    
    # ===========================================
    # IMAGE FLICKER EFFECT (OPTIMIZED)
    # ===========================================
    
    last_flicker_time = 0
    flicker_cooldown = 0.3  # Minimum time between flickers
    
    def image_flicker_effect():
        """Optimized image flicker effect"""
        nonlocal last_flicker_time
        
        try:
            current_time = time.time()
            
            # Skip if too soon since last flicker
            if current_time - last_flicker_time < flicker_cooldown:
                window.after(random.randint(100, 500), image_flicker_effect)
                return
            
            if window.winfo_exists() and image_label and flicker_images:
                # Randomly select a flicker image
                flicker_image = random.choice(flicker_images)
                
                # Change the image label to show flicker version
                image_label.config(image=flicker_image)
                image_label.image = flicker_image  # Keep reference
                
                last_flicker_time = current_time
                
                # Random flicker duration (very short for strobe effect)
                flicker_duration = random.randint(30, 80)  # Reduced from 30-120
                
                # Return to original image after flicker duration
                window.after(flicker_duration, return_to_original_image)
                
                # Schedule next flicker with random interval
                next_flicker = random.randint(300, 800)  # Reduced frequency
                window.after(next_flicker, image_flicker_effect)
        except Exception as e:
            # Silently fail and retry
            if window.winfo_exists():
                window.after(500, image_flicker_effect)
    
    def return_to_original_image():
        """Return to original image after flicker"""
        try:
            if window.winfo_exists() and image_label and original_photo:
                image_label.config(image=original_photo)
                image_label.image = original_photo
        except:
            pass
    
    # Start image flicker effect with delay
    if image_label and flicker_images:
        window.after(1000, image_flicker_effect)
    
    # ===========================================
    # EPIC FINAL SCARE - FULL SCREEN EXTENSION
    # ===========================================
    
    def create_full_screen_scare():
        """Create a terrifying full-screen version of the image"""
        try:
            if not full_screen_image:
                return None
            
            # Create extremely enhanced version for the scare
            scary_image = full_screen_image.copy()
            
            # Dramatic enhancements
            # 1. Extreme contrast
            enhancer = ImageEnhance.Contrast(scary_image)
            scary_image = enhancer.enhance(3.0)
            
            # 2. Blood red tint
            r, g, b = scary_image.split()
            r = r.point(lambda i: min(i * 2.5, 255))  # Extreme red
            g = g.point(lambda i: i * 0.1)  # Almost no green
            b = b.point(lambda i: i * 0.1)  # Almost no blue
            scary_image = Image.merge('RGB', (r, g, b))
            
            # 3. Add glowing eyes effect
            scary_image = scary_image.filter(ImageFilter.GaussianBlur(radius=0.5))
            enhancer = ImageEnhance.Brightness(scary_image)
            scary_image = enhancer.enhance(1.3)
            
            # Resize to full screen
            scary_image = scary_image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(scary_image)
        except Exception as e:
            print(f"[ERROR] Failed to create full screen scare image: {e}")
            return None
    
    # ===========================================
    # OPTIMIZED EYE EFFECT
    # ===========================================
    
    class OptimizedScaryEye:
        def __init__(self, canvas, x, y, size):
            self.canvas = canvas
            self.x = x
            self.y = y
            self.size = size
            self.blink_timer = 0
            self.blink_state = 0
            self.direction_x = random.choice([-1, 1]) * random.uniform(0.3, 1.5)  # Slower
            self.direction_y = random.choice([-1, 1]) * random.uniform(0.3, 1.5)  # Slower
            
            # Draw eye with simplified glow effect
            self.glow = canvas.create_oval(x-size*1.3, y-size*0.6, 
                                           x+size*1.3, y+size*0.6,
                                           fill='#FF3333', outline='', width=0)
            self.white = canvas.create_oval(x-size, y-size//2, 
                                           x+size, y+size//2,
                                           fill='#FFFFFF', outline='', width=0)
            pupil_size = size // 3
            self.pupil = canvas.create_oval(x-pupil_size, y-pupil_size//2,
                                           x+pupil_size, y+pupil_size//2,
                                           fill='#000000', outline='', width=0)
            
        def update_position(self):
            # Slower, smoother movement
            self.x += self.direction_x
            self.y += self.direction_y
            
            # Bounce off edges
            if self.x < self.size*2 or self.x > window_width - self.size*2:
                self.direction_x *= -0.8  # Dampen bounce
            
            if self.y < self.size*2 or self.y > window_height - self.size*2:
                self.direction_y *= -0.8  # Dampen bounce
            
            # Update positions
            self.canvas.coords(self.glow, 
                              self.x-self.size*1.3, self.y-self.size*0.6,
                              self.x+self.size*1.3, self.y+self.size*0.6)
            self.canvas.coords(self.white,
                              self.x-self.size, self.y-self.size//2,
                              self.x+self.size, self.y+self.size//2)
            pupil_size = self.size // 3
            self.canvas.coords(self.pupil,
                              self.x-pupil_size, self.y-pupil_size//2,
                              self.x+pupil_size, self.y+pupil_size//2)
        
        def update_blink(self):
            self.blink_timer += 1
            if self.blink_timer >= random.randint(30, 60):  # Less frequent blinking
                self.blink_timer = 0
                self.blink_state = (self.blink_state + 1) % 3
                
                if self.blink_state == 1:  # Half closed
                    self.canvas.coords(self.white,
                                      self.x-self.size, self.y-self.size//3,
                                      self.x+self.size, self.y+self.size//3)
                elif self.blink_state == 2:  # Closed
                    self.canvas.coords(self.white,
                                      self.x-self.size, self.y-1,
                                      self.x+self.size, self.y+1)
                else:  # Open
                    self.canvas.coords(self.white,
                                      self.x-self.size, self.y-self.size//2,
                                      self.x+self.size, self.y+self.size//2)
    
    eyes = []
    
    def add_eye_effect():
        try:
            if window.winfo_exists():
                canvas = tk.Canvas(window, bg='', highlightthickness=0)
                canvas.place(x=0, y=0, width=window_width, height=window_height)
                active_canvases.append(canvas)
                
                # Fewer eyes for better performance
                for _ in range(random.randint(1, 2)):
                    x = random.randint(50, window_width - 50)
                    y = random.randint(50, window_height - 50)
                    size = random.randint(15, 30)
                    
                    eye = OptimizedScaryEye(canvas, x, y, size)
                    eyes.append((eye, canvas))
                
                def animate_eyes():
                    if window.winfo_exists():
                        for eye, canv in eyes[:]:
                            if canv.winfo_exists():
                                eye.update_position()
                                eye.update_blink()
                        
                        # Slower animation (every 100ms instead of 50ms)
                        window.after(100, animate_eyes)
                
                animate_eyes()
                
                # Remove after shorter time
                window.after(random.randint(1500, 3000), 
                           lambda c=canvas: remove_canvas(c))
        except:
            pass
    
    def remove_canvas(canvas):
        try:
            if canvas.winfo_exists():
                canvas.destroy()
            if canvas in active_canvases:
                active_canvases.remove(canvas)
            global eyes
            eyes = [(eye, canv) for eye, canv in eyes if canv != canvas]
        except:
            pass
    
    def trigger_eyes():
        try:
            if window.winfo_exists():
                add_eye_effect()
                # Less frequent eye appearances
                window.after(random.randint(3000, 6000), trigger_eyes)
        except:
            pass
    
    # Start eye effects after a delay
    window.after(1500, trigger_eyes)
    
    # ===========================================
    # FINAL EPIC SCARE SEQUENCE - MODIFIED FOR 12 SECONDS
    # ===========================================
    
    def epic_final_scare():
        """Epic final scare with full screen extension - 12 second version"""
        nonlocal animation_active, full_screen_photo
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [SCARE] Starting epic final scare sequence (12-second version)!")
        
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
                # Phase 1: Intense shaking (reduced duration for 12-second total)
                print("[SCARE] Phase 1: Intense shaking")
                intense_shake(0)
                
            elif step == 1:
                # Phase 2: Rapid flicker (reduced duration)
                print("[SCARE] Phase 2: Rapid flicker")
                rapid_flicker(0)
                
            elif step == 2:
                # Phase 3: Full screen extension
                print("[SCARE] Phase 3: Full screen extension!")
                extend_to_full_screen()
                
            elif step == 3:
                # Phase 4: Hold full screen scare (reduced duration)
                print("[SCARE] Phase 4: Hold full screen")
                window.after(600, final_destroy)
        
        def intense_shake(count=0):
            if count >= 15 or not window.winfo_exists():  # Reduced from 20
                window.after(300, lambda: scare_sequence(1))
                return
            
            # Extreme shaking
            shake_x = random.randint(-30, 30)
            shake_y = random.randint(-20, 20)
            
            current_width = window.winfo_width()
            current_height = window.winfo_height()
            current_x = window.winfo_x()
            current_y = window.winfo_y()
            
            window.geometry(f"{current_width}x{current_height}+{current_x+shake_x}+{current_y+shake_y}")
            
            # Rapid image flicker during shake
            if image_label and flicker_images and count % 2 == 0:
                flicker_image = random.choice([flicker_images[0], flicker_images[5]])  # Red versions
                image_label.config(image=flicker_image)
                image_label.image = flicker_image
            
            window.after(60, lambda: intense_shake(count + 1))  # Slightly faster
        
        def rapid_flicker(count=0):
            if count >= 10 or not window.winfo_exists():  # Reduced from 15
                window.after(200, lambda: scare_sequence(2))
                return
            
            # Ultra-fast flicker between red and original
            if image_label and flicker_images:
                if count % 2 == 0:
                    image_label.config(image=flicker_images[0])  # Bright red
                else:
                    image_label.config(image=original_photo)
            
            window.after(50, lambda: rapid_flicker(count + 1))  # Faster flicker
        
        def extend_to_full_screen():
            """Smooth extension to full screen with terrifying image"""
            if not window.winfo_exists():
                return
            
            # Create full screen scare image
            full_screen_photo = create_full_screen_scare()
            
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
            
            # Animate expansion (faster for 12-second total)
            def expand_frame(frame=0):
                if frame > 25 or not window.winfo_exists():  # Reduced from 30
                    # Final frame: set to full screen
                    window.geometry(f"{target_width}x{target_height}+{target_x}+{target_y}")
                    
                    # Switch to full screen scary image
                    if full_screen_photo and image_label:
                        image_label.config(image=full_screen_photo)
                        image_label.image = full_screen_photo
                        image_label.place(x=0, y=0, width=target_width, height=target_height)
                    
                    window.after(400, lambda: scare_sequence(3))  # Reduced wait
                    return
                
                # Calculate intermediate size (ease-out)
                t = frame / 25  # Adjusted for new frame count
                t = t * t  # Ease-out
                
                current_width = int(start_width + (target_width - start_width) * t)
                current_height = int(start_height + (target_height - start_height) * t)
                current_x = int(start_x + (target_x - start_x) * t)
                current_y = int(start_y + (target_y - start_y) * t)
                
                window.geometry(f"{current_width}x{current_height}+{current_x}+{current_y}")
                
                # Update image size
                if image_label:
                    image_label.place(x=0, y=0, width=current_width, height=current_height)
                
                window.after(16, lambda: expand_frame(frame + 1))  # ~60 FPS
            
            expand_frame()
        
        # Start the scare sequence
        scare_sequence(0)
    
    def final_destroy():
        """Final cleanup"""
        try:
            # Return to original image briefly
            if image_label and original_photo:
                image_label.config(image=original_photo)
                image_label.image = original_photo
            
            # Flash white before closing
            window.configure(bg='#FFFFFF')
            window.update()
            time.sleep(0.1)
            
            # Clean up
            for canvas in active_canvases[:]:
                try:
                    if canvas.winfo_exists():
                        canvas.destroy()
                except:
                    pass
            
            if window.winfo_exists():
                window.destroy()
                
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] 12-second epic scare completed!")
                
        except Exception as e:
            print(f"[ERROR] Final destroy error: {e}")
    
    # Schedule epic scare after 12 seconds TOTAL (adjusting for buildup time)
    # We've had about 1 second of initial animations, so start final scare at 11 seconds
    window.after(11000, epic_final_scare)
    
    # Print to console
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] [INFO] SCARY WINDOW ACTIVATED - 12 SECOND VERSION")
    print(f"[{current_time}] [INFO] Screen size: {screen_width}x{screen_height}")
    print(f"[{current_time}] [INFO] Window size: {window_width}x{window_height}")
    print(f"[{current_time}] [INFO] Smooth shaking and pulsing animations active")
    print(f"[{current_time}] [INFO] Epic full-screen scare in 12 seconds total")
    
    # Bind escape key to close window (for safety)
    def on_escape(event):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Escape pressed, closing window")
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
