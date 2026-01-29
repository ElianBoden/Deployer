
import tkinter as tk
import math
import time

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
    "text": "Je te vois",              # Text to display (use \n for line breaks)
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
    "always_on_top": True,              # Keep window on top of other windows
    
    # Interaction settings
    "draggable": True,                   # Allow window to be dragged
    "close_button": True,                # Show close button
    "escape_to_close": True,             # Press Escape to close window
    "auto_center_text": True,            # Automatically center text in window
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
        
        # Store original dimensions for breathing effect
        self.original_width = window_width
        self.original_height = window_height
        self.original_x = x_pos
        self.original_y = y_pos
        
        # Animation variables
        self.breath_time = 0
        self.text_time = 0
        
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
                command=self.root.destroy,
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
            self.root.bind('<Escape>', lambda e: self.root.destroy())
        
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
    
    def animate(self):
        """Update the breathing and text movement animations"""
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
