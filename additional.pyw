
import tkinter as tk
import requests
import random
import time
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw, ImageFont
from typing import List, Optional, Tuple, Dict
import threading
import concurrent.futures

class CrazyFlickeringImages:
    """Optimized crazy flickering animation with multiple images and random behavior"""
    
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
            'duration': None,  # Total duration in seconds (None = infinite)
            'start_delay': 1000,  # ms before starting
            
            # Visual effects
            'rotation_range': (-15, 15),  # Degrees to rotate images
            'opacity_range': (0.3, 1.0),  # Random opacity
            'color_tint': False,  # Random color tinting
            
            # Performance settings
            'preload_images': True,
            'max_threads': 4,
            'cache_images': True,
        }
        
        # Update with custom config
        if config:
            self.config.update(config)
        
        # State variables
        self.root = None
        self.images: List[tk.PhotoImage] = []
        self.image_positions: List[Tuple[int, int]] = []
        self.visible_images: Dict[int, Dict] = {}  # id: {canvas_id, end_time, position}
        self.next_image_id = 0
        self.running = False
        self.start_time = None
        
        # Performance optimization
        self.canvas = None
        self.image_cache: Dict[str, tk.PhotoImage] = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.config['max_threads'])
        
        # Load images in background if enabled
        if self.config['preload_images']:
            self.preload_all_images()
    
    def preload_all_images(self):
        """Preload all images in background threads"""
        print(f"Preloading {len(self.config['image_urls'])} images...")
        futures = []
        for url in self.config['image_urls']:
            future = self.executor.submit(self.load_image, url)
            futures.append(future)
        
        # Wait for all to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                img = future.result()
                if img:
                    self.images.append(img)
            except Exception as e:
                print(f"Error preloading image: {e}")
    
    def load_image(self, url: str) -> Optional[tk.PhotoImage]:
        """Load and cache an image from URL"""
        if url in self.image_cache and self.config['cache_images']:
            return self.image_cache[url]
        
        try:
            response = requests.get(url, timeout=10)
            
            # Create image without screen size dependency (we'll resize later)
            pil_image = Image.open(BytesIO(response.content))
            
            # Store the original image for later resizing
            if self.config['cache_images']:
                self.image_cache[url] = pil_image
            return pil_image
            
        except Exception as e:
            print(f"Error loading image {url}: {e}")
            return None
    
    def create_window(self):
        """Create the main window"""
        self.root = tk.Tk()
        self.root.title("")
        
        if self.config['borderless']:
            self.root.overrideredirect(True)
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if self.config['fullscreen']:
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Make window transparent
        if self.config['transparent']:
            try:
                # Windows-specific transparency
                self.root.wm_attributes('-transparentcolor', 'black')
            except:
                pass
            try:
                # Linux/macOS transparency
                self.root.wm_attributes('-alpha', 0.01)
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
        self.calculate_positions(screen_width, screen_height)
        
        # Process images if not preloaded
        if not self.images or not self.config['preload_images']:
            self.process_images(screen_width, screen_height)
        
        # Create fallback if no images loaded
        if not self.images:
            self.create_fallback_image(screen_width, screen_height)
    
    def process_images(self, screen_width: int, screen_height: int):
        """Process and resize images for display"""
        print(f"Processing images for display...")
        cell_width = screen_width // self.config['grid_size'][0]
        cell_height = screen_height // self.config['grid_size'][1]
        target_width = int(cell_width * self.config['image_scale'])
        target_height = int(cell_height * self.config['image_scale'])
        
        for url in self.config['image_urls']:
            img = self.load_image(url)
            if img:
                # Resize image
                img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Apply rotation if enabled
                if self.config['rotation_range']:
                    angle = random.uniform(*self.config['rotation_range'])
                    img = img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)
        
        # Store reference to prevent garbage collection
        if hasattr(self, 'root'):
            self.root.processed_images = self.images
    
    def calculate_positions(self, screen_width: int, screen_height: int):
        """Calculate grid positions or random positions"""
        cols, rows = self.config['grid_size']
        
        if self.config['random_positions']:
            # Generate random positions
            num_positions = cols * rows * 3  # More positions for randomness
            cell_width = screen_width // cols
            cell_height = screen_height // rows
            
            for _ in range(num_positions):
                x = random.randint(0, screen_width - cell_width)
                y = random.randint(0, screen_height - cell_height)
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
    
    def create_fallback_image(self, screen_width: int, screen_height: int):
        """Create a fallback image if no URLs work"""
        cell_width = screen_width // self.config['grid_size'][0]
        cell_height = screen_height // self.config['grid_size'][1]
        target_width = int(cell_width * self.config['image_scale'])
        target_height = int(cell_height * self.config['image_scale'])
        
        # Create colored patterns as fallback
        colors = ['red', 'blue', 'green', 'yellow', 'purple', 'cyan', 'magenta', 'orange']
        for i, color in enumerate(colors[:3]):  # Limit to 3 fallback images
            pil_image = Image.new('RGBA', (target_width, target_height), color)
            draw = ImageDraw.Draw(pil_image)
            
            # Try to use a font
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            draw.text((target_width//2, target_height//2), f"IMG {i+1}", 
                     fill='white', font=font, anchor="mm")
            
            photo = ImageTk.PhotoImage(pil_image)
            self.images.append(photo)
        
        # Store reference
        if hasattr(self, 'root'):
            self.root.fallback_images = self.images
    
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
        
        # Clean up old images
        self.cleanup_old_images()
        
        # Add random images (sometimes multiple for intense flicker)
        num_new_images = 1
        if random.random() < 0.3:  # 30% chance for multiple images
            num_new_images = random.randint(1, 3)
        
        for _ in range(num_new_images):
            if len(self.visible_images) < self.config['max_concurrent_images']:
                self.add_random_image()
        
        # Schedule next flicker with random delay
        self.root.after(delay, self.flicker_image)
    
    def add_random_image(self):
        """Add a random image at random position"""
        if not self.images or not self.image_positions:
            return
        
        # Select random image
        image = random.choice(self.images)
        
        # Select random position
        if self.config['random_positions'] and self.image_positions:
            position = random.choice(self.image_positions)
            # Add jitter
            jitter = self.config['position_jitter']
            x = position[0] + random.randint(-jitter, jitter)
            y = position[1] + random.randint(-jitter, jitter)
        elif self.image_positions:
            position = random.choice(self.image_positions)
            x, y = position
        else:
            return
        
        # Random visible time
        visible_time = random.randint(self.config['min_visible_time'],
                                    self.config['max_visible_time'])
        
        # Create image on canvas
        image_id = self.canvas.create_image(x, y, image=image, anchor='nw', tags=f"image_{self.next_image_id}")
        
        # Store image info
        self.visible_images[self.next_image_id] = {
            'id': image_id,
            'end_time': time.time() * 1000 + visible_time,
            'position': (x, y)
        }
        
        # Schedule removal with random delay variation
        removal_delay = visible_time + random.randint(-50, 50)
        self.root.after(max(10, removal_delay), 
                       lambda iid=self.next_image_id: self.remove_image(iid))
        
        self.next_image_id += 1
    
    def remove_image(self, image_id: int):
        """Remove a specific image"""
        if image_id in self.visible_images:
            info = self.visible_images[image_id]
            self.canvas.delete(info['id'])
            del self.visible_images[image_id]
            
            # Occasionally make it reappear elsewhere immediately
            if random.random() < 0.1 and self.running:
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
        print(f"Flicker intensity: {self.config['flicker_intensity']}")
        print(f"Max concurrent images: {self.config['max_concurrent_images']}")
        print(f"Delay range: {self.config['min_flicker_delay']}-{self.config['max_flicker_delay']}ms")
        print("-" * 60)
        print("Controls:")
        print("  ESC - Exit")
        print("  SPACE - Pause/Resume")
        print("  +/= - Increase intensity")
        print("  -/_ - Decrease intensity")
        print("  R - Reset (clear all images)")
        print("  F - Faster flickering")
        print("  S - Slower flickering")
        print("=" * 60)
        
        # Bind controls
        self.root.bind('<Escape>', lambda e: self.stop())
        self.root.bind('<space>', lambda e: self.toggle_pause())
        self.root.bind('<plus>', lambda e: self.adjust_intensity(0.1))
        self.root.bind('<equal>', lambda e: self.adjust_intensity(0.1))
        self.root.bind('<minus>', lambda e: self.adjust_intensity(-0.1))
        self.root.bind('<underscore>', lambda e: self.adjust_intensity(-0.1))
        self.root.bind('r', lambda e: self.reset())
        self.root.bind('R', lambda e: self.reset())
        self.root.bind('f', lambda e: self.adjust_speed(-0.1))
        self.root.bind('F', lambda e: self.adjust_speed(-0.1))
        self.root.bind('s', lambda e: self.adjust_speed(0.1))
        self.root.bind('S', lambda e: self.adjust_speed(0.1))
        
        # Start flickering after delay
        self.root.after(self.config['start_delay'], self.flicker_image)
        
        # Start duration timer if set
        if self.config['duration']:
            self.root.after(self.config['duration'] * 1000, self.stop)
        
        # Start FPS/performance monitoring
        self.root.after(1000, self.monitor_performance)
        
        # Start main loop
        self.root.mainloop()
    
    def stop(self):
        """Stop the animation"""
        self.running = False
        self.executor.shutdown(wait=False)
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
        self.config['flicker_intensity'] = max(0.1, min(1.0, new_intensity))
        print(f"Intensity: {self.config['flicker_intensity']:.1f}")
    
    def adjust_speed(self, delta: float):
        """Adjust flicker speed"""
        factor = 1.0 + delta
        self.config['min_flicker_delay'] = max(5, int(self.config['min_flicker_delay'] * factor))
        self.config['max_flicker_delay'] = max(10, int(self.config['max_flicker_delay'] * factor))
        print(f"Speed: {self.config['min_flicker_delay']}-{self.config['max_flicker_delay']}ms")
    
    def reset(self):
        """Reset animation - clear all images"""
        # Clear all images from canvas
        self.canvas.delete("all")
        self.visible_images.clear()
        print("Reset - all images cleared")
    
    def monitor_performance(self):
        """Monitor and display performance info"""
        if self.running:
            fps = len(self.visible_images)  # Rough FPS estimate
            print(f"Performance: {fps} images visible, {self.next_image_id} total created")
            self.root.after(5000, self.monitor_performance)


# Enhanced preset configurations
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
        'preload_images': True,
    },
    
    'subtle': {
        'min_flicker_delay': 100,
        'max_flicker_delay': 500,
        'min_visible_time': 500,
        'max_visible_time': 3000,
        'max_concurrent_images': 8,
        'flicker_intensity': 0.3,
        'position_jitter': 5,
        'rotation_range': None,
        'preload_images': True,
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
        'preload_images': True,
    },
    
    'chaos': {
        'min_flicker_delay': 1,
        'max_flicker_delay': 30,
        'min_visible_time': 10,
        'max_visible_time': 500,
        'max_concurrent_images': 50,
        'flicker_intensity': 0.95,
        'position_jitter': 100,
        'rotation_range': (-180, 180),
        'preload_images': True,
        'image_scale': 0.5,  # Smaller images for more chaos
    }
}


def start_crazy_flickering(config_name: str = 'crazy', 
                          custom_urls: List[str] = None,
                          custom_config: Dict = None):
    """Start the flickering animation with custom settings"""
    
    # Start with preset
    config = CONFIG_PRESETS.get(config_name, CONFIG_PRESETS['crazy']).copy()
    
    # Update with custom URLs
    if custom_urls:
        config['image_urls'] = custom_urls
    
    # Update with custom config
    if custom_config:
        config.update(custom_config)
    
    # Create and start animation
    animation = CrazyFlickeringImages(config)
    animation.start()


# Example usage with different image sources
EXAMPLE_IMAGE_URLS = {
    'memes': [
        "https://i.imgur.com/8nLf3M8.jpg",
        "https://i.imgur.com/9pH5bYq.jpg",
        "https://i.imgur.com/7Q1W7yF.jpg",
    ],
    'nature': [
        "https://images.unsplash.com/photo-1501854140801-50d01698950b",
        "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07",
        "https://images.unsplash.com/photo-1439066615861-d1af74d74000",
    ],
    'abstract': [
        "https://images.unsplash.com/photo-1541701494587-cb58502866ab",
        "https://images.unsplash.com/photo-1519681393784-d120267933ba",
        "https://images.unsplash.com/photo-1550684376-efcbd6e3f031",
    ]
}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crazy flickering image animation")
    parser.add_argument('--preset', choices=CONFIG_PRESETS.keys(), default='crazy',
                       help='Animation preset (default: crazy)')
    parser.add_argument('--urls', nargs='+', help='Custom image URLs')
    parser.add_argument('--intensity', type=float, help='Flicker intensity (0.0 to 1.0)')
    parser.add_argument('--speed', type=float, help='Speed factor (0.1 to 10.0)')
    parser.add_argument('--max-images', type=int, help='Maximum concurrent images')
    
    args = parser.parse_args()
    
    # Build custom config
    custom_config = {}
    if args.intensity:
        custom_config['flicker_intensity'] = max(0.0, min(1.0, args.intensity))
    if args.speed:
        custom_config['min_flicker_delay'] = max(1, int(50 / args.speed))
        custom_config['max_flicker_delay'] = max(10, int(200 / args.speed))
    if args.max_images:
        custom_config['max_concurrent_images'] = max(1, args.max_images)
    
    # Use provided URLs or example URLs
    urls = args.urls or CONFIG_PRESETS[args.preset].get('image_urls', [])
    
    # Start the animation
    print("Starting Crazy Flickering Animation...")
    print(f"Preset: {args.preset}")
    print(f"Images: {len(urls)}")
    
    try:
        start_crazy_flickering(args.preset, urls, custom_config)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
