import tkinter as tk
import requests
import random
import time
from io import BytesIO
from PIL import Image, ImageTk
from typing import List, Optional, Tuple, Dict
import threading

class CrazyFlickeringImages:
    """Crazy flickering animation with multiple images and random behavior"""
    
    def __init__(self, config: Optional[Dict] = None):
        # Default configuration
        self.config = {
            # Window settings
            'fullscreen': True,
            'transparent': True,
            'topmost': True,
            'borderless': True,
            
            # Image settings
            'image_urls': [
                "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg",
                "https://images.unsplash.com/photo-1579546929662-711aa81148cf",
                "https://images.unsplash.com/photo-1550745165-9bc0b252726f",
            ],
            'grid_size': (10, 5),  # columns, rows
            'image_scale': 0.9,  # Scale factor for images (0.0 to 1.0)
            
            # Animation settings
            'min_flicker_delay': 20,  # ms between new images
            'max_flicker_delay': 200,  # ms between new images
            'min_visible_time': 100,  # ms image stays visible
            'max_visible_time': 2000,  # ms image stays visible
            'max_concurrent_images': 15,  # Max images visible at once
            'flicker_intensity': 0.7,  # 0.0 to 1.0 (higher = more intense)
            
            # Random position settings
            'random_positions': True,
            'allow_overlap': True,
            'position_jitter': 10,  # Random position offset
            
            # Control settings
            'duration': 5,  # Total duration in seconds (None = infinite)
            'start_delay': 1000,  # ms before starting
            
            # Visual effects
            'rotation_range': (-15, 15),  # Degrees to rotate images
            'opacity_range': (0.3, 1.0),  # Random opacity
            'color_tint': False,  # Random color tinting
        }
        
        # Update with custom config
        if config:
            self.config.update(config)
        
        # State variables
        self.root = None
        self.images: List[tk.PhotoImage] = []
        self.image_positions: List[Tuple[int, int]] = []
        self.visible_images: Dict[int, Dict] = {}  # id: {label, end_time, position}
        self.next_image_id = 0
        self.running = False
        self.start_time = None
        
        # Performance optimization
        self.canvas = None
        self.image_cache: Dict[str, tk.PhotoImage] = {}
        
    def load_image(self, url: str) -> Optional[tk.PhotoImage]:
        """Load and cache an image from URL"""
        if url in self.image_cache:
            return self.image_cache[url]
        
        try:
            response = requests.get(url, timeout=10)
            pil_image = Image.open(BytesIO(response.content))
            
            # Resize based on grid
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            cell_width = screen_width // self.config['grid_size'][0]
            cell_height = screen_height // self.config['grid_size'][1]
            
            # Apply scaling
            target_width = int(cell_width * self.config['image_scale'])
            target_height = int(cell_height * self.config['image_scale'])
            
            pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Apply random rotation if enabled
            if self.config['rotation_range']:
                angle = random.uniform(*self.config['rotation_range'])
                pil_image = pil_image.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_image)
            self.image_cache[url] = photo
            return photo
            
        except Exception as e:
            print(f"Error loading image {url}: {e}")
            return None
    
    def create_window(self):
        """Create the main window"""
        self.root = tk.Tk()
        self.root.title("")
        
        if self.config['borderless']:
            self.root.overrideredirect(True)
        
        if self.config['fullscreen']:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        if self.config['transparent']:
            try:
                self.root.wm_attributes('-transparentcolor', 'black')
            except:
                pass
        
        self.root.configure(bg='black')
        
        if self.config['topmost']:
            self.root.attributes('-topmost', True)
        
        # Create canvas for better performance
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height, 
                               bg='black', highlightthickness=0)
        self.canvas.pack()
        
        # Calculate grid positions
        self.calculate_positions()
        
        # Load images
        print(f"Loading {len(self.config['image_urls'])} images...")
        for url in self.config['image_urls']:
            img = self.load_image(url)
            if img:
                self.images.append(img)
        
        if not self.images:
            print("No images loaded, creating fallback...")
            self.create_fallback_image()
    
    def calculate_positions(self):
        """Calculate grid positions or random positions"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        cols, rows = self.config['grid_size']
        
        if self.config['random_positions']:
            # Generate random positions
            num_positions = cols * rows * 2  # More positions for randomness
            for _ in range(num_positions):
                x = random.randint(0, screen_width - 100)
                y = random.randint(0, screen_height - 100)
                self.image_positions.append((x, y))
        else:
            # Grid positions
            cell_width = screen_width // cols
            cell_height = screen_height // rows
            for i in range(cols * rows):
                row = i // cols
                col = i % cols
                x = col * cell_width
                y = row * cell_height
                self.image_positions.append((x, y))
    
    def create_fallback_image(self):
        """Create a fallback image if no URLs work"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        cell_width = screen_width // self.config['grid_size'][0]
        cell_height = screen_height // self.config['grid_size'][1]
        
        # Create colored patterns as fallback
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'magenta', 'orange']
        for i, color in enumerate(colors):
            pil_image = Image.new('RGBA', (cell_width, cell_height), color)
            draw = ImageDraw.Draw(pil_image)
            draw.text((cell_width//2, cell_height//2), str(i+1), fill='white', 
                     font=ImageFont.load_default())
            photo = ImageTk.PhotoImage(pil_image)
            self.images.append(photo)
    
    def flicker_image(self):
        """Create a new flickering image"""
        if not self.running:
            return
        
        # Random delay for next flicker
        delay = random.randint(self.config['min_flicker_delay'], 
                             self.config['max_flicker_delay'])
        
        # Randomly skip flickers based on intensity
        if random.random() > self.config['flicker_intensity']:
            self.root.after(delay, self.flicker_image)
            return
        
        # Remove old images if we have too many
        self.cleanup_old_images()
        
        # Check if we should add new image
        if len(self.visible_images) < self.config['max_concurrent_images']:
            self.add_random_image()
        
        # Schedule next flicker
        self.root.after(delay, self.flicker_image)
    
    def add_random_image(self):
        """Add a random image at random position"""
        if not self.images or not self.image_positions:
            return
        
        # Select random image
        image = random.choice(self.images)
        
        # Select random position
        if self.config['random_positions']:
            position = random.choice(self.image_positions)
            # Add jitter
            jitter = self.config['position_jitter']
            x = position[0] + random.randint(-jitter, jitter)
            y = position[1] + random.randint(-jitter, jitter)
        else:
            position = random.choice(self.image_positions)
            x, y = position
        
        # Random visible time
        visible_time = random.randint(self.config['min_visible_time'],
                                    self.config['max_visible_time'])
        
        # Random opacity
        opacity = random.uniform(*self.config['opacity_range'])
        
        # Create image on canvas
        image_id = self.canvas.create_image(x, y, image=image, anchor='nw')
        
        # Apply opacity if supported
        try:
            if opacity < 1.0:
                self.canvas.itemconfig(image_id, state='disabled')
        except:
            pass
        
        # Store image info
        self.visible_images[self.next_image_id] = {
            'id': image_id,
            'end_time': time.time() * 1000 + visible_time,
            'position': (x, y),
            'opacity': opacity
        }
        
        # Schedule removal
        self.root.after(visible_time, lambda iid=self.next_image_id: self.remove_image(iid))
        
        self.next_image_id += 1
        
        # Occasionally add extra images for intensity
        if random.random() < 0.3 and len(self.visible_images) < self.config['max_concurrent_images'] - 1:
            self.root.after(random.randint(10, 100), self.add_random_image)
    
    def remove_image(self, image_id: int):
        """Remove a specific image"""
        if image_id in self.visible_images:
            info = self.visible_images[image_id]
            self.canvas.delete(info['id'])
            del self.visible_images[image_id]
            
            # Occasionally make it reappear elsewhere immediately
            if random.random() < 0.2 and self.running:
                self.root.after(random.randint(10, 100), self.add_random_image)
    
    def cleanup_old_images(self):
        """Remove images that have exceeded their visible time"""
        current_time = time.time() * 1000
        to_remove = []
        
        for image_id, info in self.visible_images.items():
            if current_time > info['end_time']:
                to_remove.append(image_id)
        
        for image_id in to_remove:
            self.remove_image(image_id)
    
    def start(self):
        """Start the flickering animation"""
        self.create_window()
        self.running = True
        self.start_time = time.time()
        
        print("=" * 60)
        print("CRAZY FLICKERING ANIMATION")
        print("=" * 60)
        print(f"Loaded {len(self.images)} images")
        print(f"Grid: {self.config['grid_size'][0]}x{self.config['grid_size'][1]}")
        print(f"Flicker intensity: {self.config['flicker_intensity']}")
        print(f"Max concurrent images: {self.config['max_concurrent_images']}")
        print("-" * 60)
        print("Controls:")
        print("  ESC - Exit")
        print("  SPACE - Pause/Resume")
        print("  + - Increase intensity")
        print("  - - Decrease intensity")
        print("  R - Reset")
        print("=" * 60)
        
        # Bind controls
        self.root.bind('<Escape>', lambda e: self.stop())
        self.root.bind('<space>', lambda e: self.toggle_pause())
        self.root.bind('<plus>', lambda e: self.adjust_intensity(0.1))
        self.root.bind('<minus>', lambda e: self.adjust_intensity(-0.1))
        self.root.bind('r', lambda e: self.reset())
        self.root.bind('<Configure>', lambda e: self.on_resize())
        
        # Start flickering after delay
        self.root.after(self.config['start_delay'], self.flicker_image)
        
        # Start duration timer if set
        if self.config['duration']:
            self.root.after(self.config['duration'] * 1000, self.stop)
        
        # Start main loop
        self.root.mainloop()
    
    def stop(self):
        """Stop the animation"""
        self.running = False
        if self.root:
            self.root.destroy()
        print("\nAnimation stopped")
    
    def toggle_pause(self):
        """Toggle pause state"""
        self.running = not self.running
        if self.running:
            print("Resumed")
            self.flicker_image()
        else:
            print("Paused")
    
    def adjust_intensity(self, delta: float):
        """Adjust flicker intensity"""
        new_intensity = self.config['flicker_intensity'] + delta
        self.config['flicker_intensity'] = max(0.0, min(1.0, new_intensity))
        print(f"Intensity: {self.config['flicker_intensity']:.1f}")
    
    def reset(self):
        """Reset animation"""
        # Clear all images
        for info in list(self.visible_images.values()):
            self.canvas.delete(info['id'])
        self.visible_images.clear()
        print("Reset - all images cleared")
    
    def on_resize(self):
        """Handle window resize"""
        if self.running:
            self.reset()
            self.calculate_positions()


# Example configurations
CONFIG_PRESETS = {
    'crazy': {
        'min_flicker_delay': 10,
        'max_flicker_delay': 150,
        'min_visible_time': 50,
        'max_visible_time': 1000,
        'max_concurrent_images': 20,
        'flicker_intensity': 0.9,
        'position_jitter': 30,
        'rotation_range': (-45, 45),
    },
    
    'subtle': {
        'min_flicker_delay': 100,
        'max_flicker_delay': 500,
        'min_visible_time': 500,
        'max_visible_time': 3000,
        'max_concurrent_images': 5,
        'flicker_intensity': 0.3,
        'position_jitter': 5,
        'rotation_range': None,
    },
    
    'epilepsy_warning': {
        'min_flicker_delay': 5,
        'max_flicker_delay': 50,
        'min_visible_time': 20,
        'max_visible_time': 100,
        'max_concurrent_images': 30,
        'flicker_intensity': 1.0,
        'position_jitter': 50,
        'rotation_range': (-90, 90),
    }
}


# Quick start function
def start_flickering(config_name: str = 'crazy', custom_urls: List[str] = None):
    """Quick start function with preset configurations"""
    
    # Use preset or default
    preset = CONFIG_PRESETS.get(config_name, CONFIG_PRESETS['crazy'])
    
    # Update with custom URLs if provided
    config = preset.copy()
    if custom_urls:
        config['image_urls'] = custom_urls
    
    # Create and start animation
    animation = CrazyFlickeringImages(config)
    animation.start()


# Interactive version with GUI controls
class FlickeringControlPanel:
    """Control panel for the flickering animation"""
    
    def __init__(self):
        self.animation = None
        self.config_window = None
        
    def show_controls(self):
        """Show control panel window"""
        self.config_window = tk.Tk()
        self.config_window.title("Flickering Animation Controls")
        self.config_window.geometry("400x500")
        
        tk.Label(self.config_window, text="FLICKERING ANIMATION CONTROLS", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # URL input
        tk.Label(self.config_window, text="Image URLs (one per line):").pack(pady=5)
        url_text = tk.Text(self.config_window, height=5, width=50)
        url_text.pack(pady=5)
        url_text.insert("1.0", "\n".join(CONFIG_PRESETS['crazy']['image_urls']))
        
        # Preset selection
        tk.Label(self.config_window, text="Preset:").pack(pady=5)
        preset_var = tk.StringVar(value="crazy")
        for preset in CONFIG_PRESETS.keys():
            tk.Radiobutton(self.config_window, text=preset.title(), 
                          variable=preset_var, value=preset).pack()
        
        # Custom intensity
        tk.Label(self.config_window, text="Custom Intensity (0.0 to 1.0):").pack(pady=5)
        intensity_var = tk.DoubleVar(value=0.7)
        intensity_scale = tk.Scale(self.config_window, from_=0.0, to=1.0, 
                                  resolution=0.1, orient=tk.HORIZONTAL,
                                  variable=intensity_var)
        intensity_scale.pack(pady=5)
        
        # Start button
        def start_animation():
            urls = [url.strip() for url in url_text.get("1.0", "end").split("\n") if url.strip()]
            preset_name = preset_var.get()
            
            config = CONFIG_PRESETS[preset_name].copy()
            config['image_urls'] = urls
            config['flicker_intensity'] = intensity_var.get()
            
            self.config_window.destroy()
            self.animation = CrazyFlickeringImages(config)
            self.animation.start()
        
        tk.Button(self.config_window, text="START ANIMATION", 
                 command=start_animation, bg="red", fg="white",
                 font=("Arial", 12, "bold")).pack(pady=20)
        
        self.config_window.mainloop()


# Command line version
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crazy flickering image animation")
    parser.add_argument('--preset', choices=CONFIG_PRESETS.keys(), default='crazy',
                       help='Animation preset')
    parser.add_argument('--gui', action='store_true', help='Show control panel')
    parser.add_argument('--url', action='append', help='Image URLs (can be used multiple times)')
    
    args = parser.parse_args()
    
    if args.gui:
        # Show control panel
        panel = FlickeringControlPanel()
        panel.show_controls()
    else:
        # Use command line args
        urls = args.url or CONFIG_PRESETS[args.preset]['image_urls']
        start_flickering(args.preset, urls)
