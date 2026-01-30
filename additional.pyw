import tkinter as tk
import math
import time
import random
from PIL import Image, ImageTk
import urllib.request
import io
import threading

# ============================================================================
# CONFIGURATION SECTION - EDIT THESE VALUES TO CUSTOMIZE THE WINDOW
# ============================================================================

CONFIG = {
    # Window settings
    "window_title": "Breathing Window",  # Title shown in taskbar (if not borderless)
    "window_size_percent": 0.7,          # Size as percentage of screen (0.7 = 70%)
    "borderless": True,                   # Remove window borders and title bar
    "background_color": "black",          # Window background color
    
    # Text settings
    "text": "C'est pas bien Alexandre",                 # Text to display (use \n for line breaks)
    "text_color": "white",               # Main text color
    "outline_color": "red",              # Outline/stroke color
    "outline_width": 4,                  # Thickness of outline (in pixels)
    "font_family": "Arial",              # Font family
    "font_size": 60,                     # Font size
    "font_weight": "bold",               # Font weight (normal, bold, etc.)
    
    # Breathing animation settings
    "breathing_enabled": True,           # Enable/disable window breathing
    "breath_amplitude": 0.03,            # Size variation (0.03 = 3% expansion/contraction)
    "breath_speed": 0.5,                 # Speed of breathing animation (higher = faster)
    
    # Text movement settings
    "text_movement_enabled": True,       # Enable/disable text up-down movement
    "text_move_amplitude": 20,           # Pixels to move text up/down
    "text_move_speed": 0.8,              # Speed of text movement (higher = faster)
    
    # Position settings
    "position": "center",                # Window position: "center" or (x, y) coordinates
    "always_on_top": True,               # Keep window on top of other windows
    
    # Interaction settings
    "draggable": True,                   # Allow window to be dragged
    "close_button": True,                # Show close button
    "escape_to_close": True,             # Press Escape to close window
    "auto_center_text": True,            # Automatically center text in window
    
    # Close image settings
    "close_image_url": "https://images.unsplash.com/photo-1582266255765-fa5cf1a1d501?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    "close_image_duration": 2000,        # Duration to show image in milliseconds
    "preload_image": True,               # Preload image on startup to avoid delay
    "show_close_animation": True,        # Show animation before image (implode/explode/fade)
    "close_animation_type": "fade",   # Animation before image: "implode", "explode", "fade", "none"
}

# ============================================================================
# END OF CONFIGURATION - DON'T EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

class BreathingWindow:
    def __init__(self, config):
        # Store config
        self.config = config
        
        # Image loading variables
        self.close_image_loaded = False
        self.close_image = None
        self.close_image_photo = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(config["window_title"])
        self.root.configure(bg=config["background_color"])
        
        # Remove window decorations if requested
        if config["borderless"]:
            self.root.overrideredirect(True)
        
        # Set always on top if requested
        if config["always_on_top"]:
            self.root.attributes('-topmost', True)
        
        # Enable transparency for fade effects
        self.root.attributes('-alpha', 1.0)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate window size
        window_width = int(screen_width * config["window_size_percent"])
        window_height = int(screen_height * config["window_size_percent"])
        
        # Calculate position
        if config["position"] == "center":
            x_pos = (screen_width - window_width) // 2
            y_pos = (screen_height - window_height) // 2
        else:
            x_pos, y_pos = config["position"]
        
        # Set window geometry
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        
        # Store original dimensions for animations
        self.original_width = window_width
        self.original_height = window_height
        self.original_x = x_pos
        self.original_y = y_pos
        self.original_alpha = 1.0
        
        # Animation variables
        self.breath_time = 0
        self.text_time = 0
        self.animating_close = False
        self.close_animation_start = 0
        self.particles = []
        
        # Create a canvas for custom text with outline
        self.canvas = tk.Canvas(
            self.root, 
            bg=config["background_color"], 
            highlightthickness=0,
            width=window_width,
            height=window_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add close button if requested
        if config["close_button"]:
            close_btn = tk.Button(
                self.root, 
                text="X", 
                command=self.start_close_animation,
                font=("Arial", 12, "bold"),
                fg="white",
                bg="#333333",
                activeforeground="white",
                activebackground="#555555",
                relief=tk.FLAT,
                bd=0
            )
            close_btn.place(relx=0.98, rely=0.02, anchor=tk.NE)
        
        # Create text with outline effect
        self.create_outlined_text()
        
        # Start animations
        self.animate()
        
        # Make window draggable if requested
        if config["draggable"]:
            self.make_draggable()
        
        # Bind escape key to close if requested
        if config["escape_to_close"]:
            self.root.bind('<Escape>', lambda e: self.start_close_animation())
        
        # Preload the close image in background thread
        if config["preload_image"] and config["close_image_url"]:
            threading.Thread(target=self.load_close_image, daemon=True).start()
        
    def load_close_image(self):
        """Load the close image from URL in a background thread"""
        try:
            # Download image from URL
            with urllib.request.urlopen(self.config["close_image_url"]) as response:
                image_data = response.read()
            
            # Open image with PIL
            self.close_image = Image.open(io.BytesIO(image_data))
            self.close_image_loaded = True
            print("Close image loaded successfully")
        except Exception as e:
            print(f"Failed to load close image: {e}")
            self.close_image_loaded = False
    
    def create_outlined_text(self):
        """Create text with fill and outline"""
        self.text_items = []
        
        # Get text settings from config
        text = self.config["text"]
        font_size = self.config["font_size"]
        font_family = self.config["font_family"]
        font_weight = self.config["font_weight"]
        
        # Center position (will be updated in animation)
        self.text_x = self.original_width // 2
        self.text_y = self.original_height // 2
        
        # Get outline settings
        outline_color = self.config["outline_color"]
        outline_width = self.config["outline_width"]
        
        # Create font tuple
        font_tuple = (font_family, font_size, font_weight)
        
        # Draw outline first (multiple layers for thickness)
        if outline_width > 0:
            # Draw outline in a circle pattern for smoother outline
            for angle in range(0, 360, 30):  # 12 points around the circle
                rad = math.radians(angle)
                dx = int(outline_width * math.cos(rad))
                dy = int(outline_width * math.sin(rad))
                outline_id = self.canvas.create_text(
                    self.text_x + dx,
                    self.text_y + dy,
                    text=text,
                    font=font_tuple,
                    fill=outline_color,
                    justify=tk.CENTER
                )
                self.text_items.append(outline_id)
        
        # Draw main text on top
        self.main_text_id = self.canvas.create_text(
            self.text_x,
            self.text_y,
            text=text,
            font=font_tuple,
            fill=self.config["text_color"],
            justify=tk.CENTER
        )
        self.text_items.append(self.main_text_id)
    
    def start_close_animation(self, event=None):
        """Start the closing animation sequence"""
        if self.animating_close:
            return
            
        self.animating_close = True
        self.close_animation_start = time.time()
        
        # If show_close_animation is True, play the animation first
        if self.config["show_close_animation"] and self.config["close_animation_type"] != "none":
            self.animate_close_transition()
        else:
            # Skip to showing the image immediately
            self.show_close_image()
    
    def animate_close_transition(self):
        """Animate the transition before showing the image"""
        if not self.animating_close:
            return
            
        current_time = time.time()
        elapsed = (current_time - self.close_animation_start) * 1000  # Convert to ms
        progress = min(elapsed / 500, 1.0)  # 0.5 second transition
        
        # Apply different animations based on type
        animation_type = self.config["close_animation_type"]
        
        if animation_type == "fade":
            self.animate_fade_transition(progress)
            
        elif animation_type == "implode":
            self.animate_implode_transition(progress)
            
        elif animation_type == "explode":
            self.animate_explode_transition(progress)
        
        # Check if animation is complete
        if progress >= 1.0:
            self.show_close_image()
        else:
            self.root.after(16, self.animate_close_transition)
    
    def animate_fade_transition(self, progress):
        """Fade out animation before showing image"""
        alpha = 1.0 - progress
        self.root.attributes('-alpha', alpha)
    
    def animate_implode_transition(self, progress):
        """Implode/shrink to center animation before showing image"""
        scale = 1.0 - progress
        new_width = int(self.original_width * scale)
        new_height = int(self.original_height * scale)
        
        # Keep centered
        new_x = self.original_x + (self.original_width - new_width) // 2
        new_y = self.original_y + (self.original_height - new_height) // 2
        
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
        self.canvas.config(width=new_width, height=new_height)
        
        # Fade at the end
        if progress > 0.7:
            alpha = 1.0 - ((progress - 0.7) / 0.3)
            self.root.attributes('-alpha', alpha)
    
    def animate_explode_transition(self, progress):
        """Explode animation before showing image"""
        # Create particles if not already created
        if not self.particles:
            self.create_transition_particles()
        
        # Update particles
        for particle in self.particles:
            # Move particle
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vy"] += 0.2  # Gravity
            
            # Update position
            self.canvas.coords(
                particle["id"],
                particle["x"], particle["y"],
                particle["x"] + particle["size"], 
                particle["y"] + particle["size"]
            )
        
        # Fade main window
        alpha = 1.0 - progress * 1.5
        if alpha > 0:
            self.root.attributes('-alpha', alpha)
        
        # Shrink window
        scale = 1.0 - progress * 0.5
        new_width = int(self.original_width * scale)
        new_height = int(self.original_height * scale)
        new_x = self.original_x + (self.original_width - new_width) // 2
        new_y = self.original_y + (self.original_height - new_height) // 2
        
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
    
    def create_transition_particles(self):
        """Create particles for explosion transition"""
        self.particles = []
        num_particles = 50
        
        for _ in range(num_particles):
            # Create a particle at random position
            x = random.randint(0, self.original_width)
            y = random.randint(0, self.original_height)
            size = random.randint(3, 10)
            color = random.choice([self.config["text_color"], 
                                  self.config["outline_color"],
                                  "white", "red", "orange"])
            
            # Random velocity
            angle = random.random() * 2 * math.pi
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Create particle on canvas
            particle = self.canvas.create_oval(
                x, y, x + size, y + size,
                fill=color, outline=color
            )
            
            self.particles.append({
                "id": particle,
                "x": x,
                "y": y,
                "vx": vx,
                "vy": vy,
                "size": size
            })
    
    def show_close_image(self):
        """Show the close image in full screen for 2 seconds"""
        # Hide the main window
        self.root.withdraw()
        
        # Create a new fullscreen window for the image
        self.image_window = tk.Toplevel()
        self.image_window.attributes('-fullscreen', True)
        self.image_window.attributes('-topmost', True)
        self.image_window.configure(bg='black')
        
        # Remove window decorations
        self.image_window.overrideredirect(True)
        
        # Get screen dimensions
        screen_width = self.image_window.winfo_screenwidth()
        screen_height = self.image_window.winfo_screenheight()
        
        # Create a canvas for the image
        image_canvas = tk.Canvas(
            self.image_window,
            bg='black',
            highlightthickness=0,
            width=screen_width,
            height=screen_height
        )
        image_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Try to load and display the image
        if self.close_image_loaded and self.close_image:
            try:
                # Resize image to fit screen while maintaining aspect ratio
                img = self.close_image.copy()
                img.thumbnail((screen_width, screen_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.close_image_photo = ImageTk.PhotoImage(img)
                
                # Calculate position to center the image
                img_width = img.width
                img_height = img.height
                x_pos = (screen_width - img_width) // 2
                y_pos = (screen_height - img_height) // 2
                
                # Display the image
                image_canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=self.close_image_photo)
                
                # Add a subtle fade-in effect
                self.image_window.attributes('-alpha', 0)
                self.fade_in_image_window()
                
            except Exception as e:
                print(f"Failed to display image: {e}")
                self.show_error_message(image_canvas, screen_width, screen_height)
        else:
            # Image not loaded, show error or fallback
            self.show_error_message(image_canvas, screen_width, screen_height)
        
        # Bind escape key to close image window immediately
        self.image_window.bind('<Escape>', lambda e: self.close_all_windows())
        
        # Schedule window to close after duration
        self.image_window.after(self.config["close_image_duration"], self.close_all_windows)
    
    def fade_in_image_window(self):
        """Fade in the image window smoothly"""
        current_alpha = self.image_window.attributes('-alpha')
        if current_alpha < 1.0:
            new_alpha = min(1.0, current_alpha + 0.05)
            self.image_window.attributes('-alpha', new_alpha)
            self.image_window.after(20, self.fade_in_image_window)
    
    def show_error_message(self, canvas, screen_width, screen_height):
        """Show an error message if image fails to load"""
        canvas.create_text(
            screen_width // 2,
            screen_height // 2,
            text="Image Failed to Load\nClosing...",
            font=("Arial", 40, "bold"),
            fill="white",
            justify=tk.CENTER
        )
    
    def close_all_windows(self):
        """Close both the image window and main window"""
        try:
            self.image_window.destroy()
        except:
            pass
        try:
            self.root.destroy()
        except:
            pass
    
    def animate(self):
        """Update the breathing and text movement animations"""
        # Skip if closing animation is running
        if self.animating_close:
            self.root.after(16, self.animate)
            return
            
        # Breathing effect for window
        if self.config["breathing_enabled"]:
            self.breath_time += self.config["breath_speed"] * 0.05
            breath_scale = 1 + self.config["breath_amplitude"] * math.sin(self.breath_time)
            
            new_width = int(self.original_width * breath_scale)
            new_height = int(self.original_height * breath_scale)
            
            # Keep window centered if it was originally centered
            if self.config["position"] == "center":
                new_x = self.original_x - (new_width - self.original_width) // 2
                new_y = self.original_y - (new_height - self.original_height) // 2
                self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
            else:
                self.root.geometry(f"{new_width}x{new_height}")
            
            # Update canvas size
            self.canvas.config(width=new_width, height=new_height)
        else:
            new_width = self.original_width
            new_height = self.original_height
        
        # Text movement (vertical oscillation)
        if self.config["text_movement_enabled"]:
            self.text_time += self.config["text_move_speed"] * 0.05
            text_offset = self.config["text_move_amplitude"] * math.sin(self.text_time)
        else:
            text_offset = 0
        
        # Update all text positions
        for text_id in self.text_items:
            current_coords = self.canvas.coords(text_id)
            if current_coords:
                if self.config["auto_center_text"]:
                    self.canvas.coords(
                        text_id, 
                        new_width // 2, 
                        (new_height // 2) + text_offset
                    )
                else:
                    # Keep original relative position
                    self.canvas.coords(
                        text_id, 
                        current_coords[0], 
                        current_coords[1] + text_offset
                    )
        
        # Schedule next animation frame (~60 FPS)
        self.root.after(16, self.animate)
    
    def make_draggable(self):
        """Make the window draggable"""
        def start_drag(event):
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        
        def do_drag(event):
            deltax = event.x - self.drag_start_x
            deltay = event.y - self.drag_start_y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
        
        # Bind events to canvas
        self.canvas.bind("<Button-1>", start_drag)
        self.canvas.bind("<B1-Motion>", do_drag)
        
        # Also bind to the text items
        for text_id in self.text_items:
            self.canvas.tag_bind(text_id, "<Button-1>", start_drag)
            self.canvas.tag_bind(text_id, "<B1-Motion>", do_drag)
    
    def run(self):
        """Start the main loop"""
        self.root.mainloop()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def create_custom_window():
    """Create and run the window with custom configuration"""
    app = BreathingWindow(CONFIG)
    app.run()

if __name__ == "__main__":
    create_custom_window()
