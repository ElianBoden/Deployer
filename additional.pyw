import tkinter as tk
import math
import time

class BreathingWindow:
    def __init__(self):
        # Create main window
        self.root = tk.Tk()
        self.root.title("Breathing Window")
        self.root.configure(bg='black')
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate 70% of screen
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.7)
        
        # Calculate position to center window
        x_pos = (screen_width - window_width) // 2
        y_pos = (screen_height - window_height) // 2
        
        # Set window geometry
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        
        # Store original dimensions for breathing effect
        self.original_width = window_width
        self.original_height = window_height
        self.original_x = x_pos
        self.original_y = y_pos
        
        # Animation variables
        self.breath_amplitude = 0.03  # 3% size variation
        self.breath_speed = 0.5  # Speed of breathing
        self.text_move_amplitude = 20  # Pixels to move text up/down
        self.text_move_speed = 0.8  # Speed of text movement
        
        self.breath_time = 0
        self.text_time = 0
        
        # Create a canvas for custom text with outline
        self.canvas = tk.Canvas(
            self.root, 
            bg='black', 
            highlightthickness=0,
            width=window_width,
            height=window_height
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add close button (optional)
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
        
        # Make window draggable
        self.make_draggable()
        
        # Bind escape key to close
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
    def create_outlined_text(self):
        """Create text with white fill and red outline"""
        self.text_items = []
        
        # Text to display
        text = "BREATHING\nWINDOW"
        font_size = 60
        font_family = "Arial"
        
        # Center position (will be updated in animation)
        self.text_x = self.original_width // 2
        self.text_y = self.original_height // 2
        
        # Create outline by drawing the text multiple times with offsets
        outline_color = "red"
        outline_width = 4
        
        # Draw outline first (multiple layers for thickness)
        for dx in range(-outline_width, outline_width + 1, 2):
            for dy in range(-outline_width, outline_width + 1, 2):
                if dx == 0 and dy == 0:
                    continue
                outline_id = self.canvas.create_text(
                    self.text_x + dx,
                    self.text_y + dy,
                    text=text,
                    font=(font_family, font_size, "bold"),
                    fill=outline_color,
                    justify=tk.CENTER
                )
                self.text_items.append(outline_id)
        
        # Draw main white text on top
        self.main_text_id = self.canvas.create_text(
            self.text_x,
            self.text_y,
            text=text,
            font=(font_family, font_size, "bold"),
            fill="white",
            justify=tk.CENTER
        )
        self.text_items.append(self.main_text_id)
    
    def animate(self):
        """Update the breathing and text movement animations"""
        current_time = time.time() * 10
        
        # Breathing effect for window
        self.breath_time += self.breath_speed
        breath_scale = 1 + self.breath_amplitude * math.sin(self.breath_time)
        
        new_width = int(self.original_width * breath_scale)
        new_height = int(self.original_height * breath_scale)
        
        # Keep window centered
        new_x = self.original_x - (new_width - self.original_width) // 2
        new_y = self.original_y - (new_height - self.original_height) // 2
        
        self.root.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
        
        # Update canvas size
        self.canvas.config(width=new_width, height=new_height)
        
        # Text movement (vertical oscillation)
        self.text_time += self.text_move_speed
        text_offset = self.text_move_amplitude * math.sin(self.text_time)
        
        # Update all text positions
        for text_id in self.text_items:
            current_coords = self.canvas.coords(text_id)
            if current_coords:
                self.canvas.coords(
                    text_id, 
                    new_width // 2, 
                    (new_height // 2) + text_offset
                )
        
        # Schedule next animation frame (60 FPS)
        self.root.after(16, self.animate)
    
    def make_draggable(self):
        """Make the window draggable"""
        def start_drag(event):
            self.x = event.x
            self.y = event.y
        
        def do_drag(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
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

if __name__ == "__main__":
    app = BreathingWindow()
    app.run()
