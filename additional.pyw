
import tkinter as tk
import math
import time
import random

# ============================================================================
# CONFIGURATION SECTION - EDIT THESE VALUES TO CUSTOMIZE THE WINDOW
# ============================================================================

CONFIG = {
    # Window settings
    "window_title": "System 32",  # Title shown in taskbar (if not borderless)
    "window_size_percent": 0.7,          # Size as percentage of screen (0.7 = 70%)
    "borderless": True,                   # Remove window borders and title bar
    "background_color": "black",          # Window background color
    
    # Text settings
    "text": "Je te vois",                 # Text to display (use \n for line breaks)
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
    
    # Close animation settings
    "close_animation": "implode",        # Animation type: "implode", "explode", "fade", 
                                         # "spin", "shatter", "melt", "wave", "random"
    "close_animation_duration": 1000,    # Duration of close animation in milliseconds
    "close_animation_color": "red",      # Color used in some animations
    "close_animation_intensity": 1.0,    # Intensity of animation (0.5 to 2.0)
}

# ============================================================================
# END OF CONFIGURATION - DON'T EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

class BreathingWindow:
    def __init__(self, config):
        # Store config
        self.config = config
        
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
        
        # Track mouse position for wave animation
        self.mouse_x = window_width // 2
        self.mouse_y = window_height // 2
        self.canvas.bind('<Motion>', self.track_mouse)
        
    def track_mouse(self, event):
        """Track mouse position for wave animation"""
        self.mouse_x = event.x
        self.mouse_y = event.y
        
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
        """Start the closing animation"""
        if self.animating_close:
            return
            
        self.animating_close = True
        self.close_animation_start = time.time()
        
        # If random animation is selected, pick one randomly
        animation_type = self.config["close_animation"]
        if animation_type == "random":
            animations = ["implode", "explode", "fade", "spin", "shatter", "melt", "wave"]
            animation_type = random.choice(animations)
            
        # Store animation type
        self.current_close_animation = animation_type
        
        # Prepare particles for explosion/shatter animations
        if animation_type in ["explode", "shatter"]:
            self.create_particles()
        
        # Start animation loop
        self.animate_close()
    
    def create_particles(self):
        """Create particles for explosion/shatter animations"""
        self.particles = []
        num_particles = 100 if self.config["close_animation"] == "explode" else 50
        
        for _ in range(num_particles):
            # Create a particle at random position
            x = random.randint(0, self.original_width)
            y = random.randint(0, self.original_height)
            size = random.randint(2, 8)
            color = random.choice([self.config["text_color"], 
                                  self.config["outline_color"], 
                                  self.config["close_animation_color"],
                                  "white", "red", "orange", "yellow"])
            
            # Random velocity
            if self.current_close_animation == "explode":
                angle = random.random() * 2 * math.pi
                speed = random.uniform(2, 8) * self.config["close_animation_intensity"]
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
            else:  # shatter
                vx = random.uniform(-5, 5) * self.config["close_animation_intensity"]
                vy = random.uniform(-5, 5) * self.config["close_animation_intensity"]
            
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
                "size": size,
                "life": 1.0
            })
    
    def animate_close(self):
        """Animate the closing effect"""
        if not self.animating_close:
            return
            
        current_time = time.time()
        elapsed = (current_time - self.close_animation_start) * 1000  # Convert to ms
        progress = min(elapsed / self.config["close_animation_duration"], 1.0)
        
        # Apply different animations based on type
        animation_type = self.current_close_animation
        
        if animation_type == "fade":
            self.animate_fade(progress)
            
        elif animation_type == "implode":
            self.animate_implode(progress)
            
        elif animation_type == "explode":
            self.animate_explode(progress)
            
        elif animation_type == "spin":
            self.animate_spin(progress)
            
        elif animation_type == "shatter":
            self.animate_shatter(progress)
            
        elif animation_type == "melt":
            self.animate_melt(progress)
            
        elif animation_type == "wave":
            self.animate_wave(progress)
        
        # Check if animation is complete
        if progress >= 1.0:
            self.root.destroy()
        else:
            self.root.after(16, self.animate_close)
    
    def animate_fade(self, progress):
        """Fade out animation"""
        alpha = 1.0 - progress
        self.root.attributes('-alpha', alpha)
        
        # Also shrink slightly
        scale = 1.0 - progress * 0.3
        self.resize_window(scale)
    
    def animate_implode(self, progress):
        """Implode/shrink to center animation"""
        scale = 1.0 - progress
        self.resize_window(scale)
        
        # Add color effect
        pulse = abs(math.sin(progress * math.pi * 3)) * 0.3 + 0.7
        self.canvas.config(bg=self.config["close_animation_color"])
        
        # Fade at the end
        if progress > 0.7:
            alpha = 1.0 - ((progress - 0.7) / 0.3)
            self.root.attributes('-alpha', alpha)
    
    def animate_explode(self, progress):
        """Explode into particles animation"""
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
            
            # Fade out
            particle["life"] -= 0.02
            if particle["life"] > 0:
                alpha_hex = hex(int(particle["life"] * 255))[2:].zfill(2)
                current_color = self.canvas.itemcget(particle["id"], "fill")
                if len(current_color) == 7:  # #RRGGBB format
                    new_color = current_color + alpha_hex
                    self.canvas.itemconfig(particle["id"], fill=new_color)
        
        # Fade main window
        alpha = 1.0 - progress * 1.5
        if alpha > 0:
            self.root.attributes('-alpha', alpha)
        
        # Shrink window
        scale = 1.0 - progress * 0.5
        self.resize_window(scale)
    
    def animate_spin(self, progress):
        """Spin and shrink animation"""
        # Calculate rotation angle
        angle = progress * 360 * 2  # Two full rotations
        
        # Convert to radians
        rad_angle = math.radians(angle)
        
        # Calculate scale (shrink while spinning)
        scale = 1.0 - progress
        
        # Resize window
        self.resize_window(scale)
        
        # Change background color
        r = int(255 * (1 - progress))
        g = int(255 * progress)
        b = int(255 * abs(math.sin(progress * math.pi)))
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.canvas.config(bg=color)
        
        # Rotate text (simulated by moving outline layers)
        radius = 20 * progress
        for i, text_id in enumerate(self.text_items):
            offset_angle = rad_angle + (i * 0.1)
            dx = math.cos(offset_angle) * radius
            dy = math.sin(offset_angle) * radius
            current_coords = self.canvas.coords(text_id)
            if current_coords:
                self.canvas.coords(
                    text_id,
                    current_coords[0] + dx,
                    current_coords[1] + dy
                )
    
    def animate_shatter(self, progress):
        """Shatter like glass animation"""
        # Move particles downward with gravity
        for particle in self.particles:
            particle["y"] += particle["vy"]
            particle["vy"] += 0.5  # Stronger gravity
            
            # Update position
            self.canvas.coords(
                particle["id"],
                particle["x"], particle["y"],
                particle["x"] + particle["size"], 
                particle["y"] + particle["size"]
            )
        
        # Make window "crack" by drawing lines
        if progress < 0.5:
            for i in range(5):
                x1 = random.randint(0, self.original_width)
                y1 = random.randint(0, self.original_height)
                x2 = x1 + random.randint(-100, 100)
                y2 = y1 + random.randint(-100, 100)
                self.canvas.create_line(x1, y1, x2, y2, 
                                      fill="white", 
                                      width=2)
        
        # Fade out
        alpha = 1.0 - progress * 1.2
        if alpha > 0:
            self.root.attributes('-alpha', alpha)
    
    def animate_melt(self, progress):
        """Melt/drip animation"""
        # Create drips
        if len(self.particles) < 50 and progress < 0.8:
            for _ in range(3):
                x = random.randint(0, self.original_width)
                size = random.randint(10, 30)
                color = random.choice([self.config["close_animation_color"], 
                                      "red", "orange", "darkred"])
                
                drip = self.canvas.create_oval(
                    x, 0, x + size, size,
                    fill=color, outline=color
                )
                
                self.particles.append({
                    "id": drip,
                    "x": x,
                    "y": 0,
                    "vy": random.uniform(5, 15) * self.config["close_animation_intensity"],
                    "size": size
                })
        
        # Move drips downward
        for particle in self.particles:
            particle["y"] += particle["vy"]
            
            # Update position
            self.canvas.coords(
                particle["id"],
                particle["x"], particle["y"],
                particle["x"] + particle["size"], 
                particle["y"] + particle["size"]
            )
        
        # Shrink window from the top
        shrink_height = int(self.original_height * progress)
        new_height = max(10, self.original_height - shrink_height)
        new_y = self.original_y + shrink_height
        
        self.root.geometry(f"{self.original_width}x{new_height}+{self.original_x}+{new_y}")
        self.canvas.config(height=new_height)
        
        # Fade out
        if progress > 0.6:
            alpha = 1.0 - ((progress - 0.6) / 0.4)
            self.root.attributes('-alpha', alpha)
    
    def animate_wave(self, progress):
        """Wave distortion animation"""
        # Create wave effect on text
        wave_amplitude = 50 * (1 - progress)
        wave_frequency = 10 * self.config["close_animation_intensity"]
        
        for i, text_id in enumerate(self.text_items):
            current_coords = self.canvas.coords(text_id)
            if current_coords:
                # Calculate wave offset
                wave_offset = math.sin(current_coords[0] * 0.1 + progress * wave_frequency) * wave_amplitude
                
                self.canvas.coords(
                    text_id,
                    current_coords[0],
                    current_coords[1] + wave_offset
                )
        
        # Change colors
        hue = progress * 360
        r = int(127 + 127 * math.sin(math.radians(hue)))
        g = int(127 + 127 * math.sin(math.radians(hue + 120)))
        b = int(127 + 127 * math.sin(math.radians(hue + 240)))
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.canvas.config(bg=color)
        
        # Shrink
        scale = 1.0 - progress * 0.7
        self.resize_window(scale)
        
        # Fade at the end
        if progress > 0.7:
            alpha = 1.0 - ((progress - 0.7) / 0.3)
            self.root.attributes('-alpha', alpha)
    
    def resize_window(self, scale):
        """Resize window by scale factor"""
        new_width = int(self.original_width * scale)
        new_height = int(self.original_height * scale)
        
        # Keep centered
        new_x = self.original_x + (self.original_width - new_width) // 2
        new_y = self.original_y + (self.original_height - new_height) // 2
        
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
        self.canvas.config(width=new_width, height=new_height)
    
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
