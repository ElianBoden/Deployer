# additional.pyw - Scary full-screen image display (Configurable)
import tkinter as tk
import urllib.request
from datetime import datetime
import sys
import random
import time
import json
import os
from typing import Optional, Tuple, Dict, Any

# ============================================================================
# CONFIGURATION TABLE - Edit these values to customize behavior
# ============================================================================

CONFIG = {
    # Image Settings
    "image_url": "https://images.unsplash.com/photo-1582266255765-fa5cf1a1d501?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D,  # Leave empty for solid color, or provide image URL
    
    # Window Settings
    "window_size_percent": 0.5,  # 0.5 = 50% of screen, 1.0 = full screen, 0.0 = small window
    "window_position": "top-left",  # "center", "random", "top-left", "top-right", "bottom-left", "bottom-right"
    "borderless": True,  # Remove window decorations
    "always_on_top": True,  # Keep window on top of others
    "background_color": "#000000",  # Fallback color if image fails
    
    # Timing Settings
    "display_duration_seconds": 10,  # How long window stays open (0 = stay open until escape)
    "close_delay_ms": 0,  # Additional delay before closing (0 = immediate)
    
    # Visual Effects Settings
    "enable_flicker": True,  # Add flickering effect
    "flicker_colors": ['#000000', '#1a0000', '#330000', '#4d0000'],  # Colors for flicker
    "flicker_min_interval": 50,  # Minimum flicker interval (ms)
    "flicker_max_interval": 300,  # Maximum flicker interval (ms)
    
    "enable_eye_effects": True,  # Add random eye appearances
    "eye_count": 3,  # Number of eyes to show at once
    "eye_min_size": 10,  # Minimum eye size (pixels)
    "eye_max_size": 30,  # Maximum eye size (pixels)
    "eye_min_duration": 500,  # Minimum time eyes stay visible (ms)
    "eye_max_duration": 2000,  # Maximum time eyes stay visible (ms)
    "eye_trigger_min": 1000,  # Minimum interval between eye effects (ms)
    "eye_trigger_max": 3000,  # Maximum interval between eye effects (ms)
    
    "enable_glitch_effects": True,  # Add screen glitch effects
    "glitch_min_count": 2,  # Minimum number of glitch lines
    "glitch_max_count": 5,  # Maximum number of glitch lines
    "glitch_width_min": 20,  # Minimum glitch line width (pixels)
    "glitch_width_max": 100,  # Maximum glitch line width (pixels)
    "glitch_height_min": 2,  # Minimum glitch line height (pixels)
    "glitch_height_max": 5,  # Maximum glitch line height (pixels)
    "glitch_color": "#FF0000",  # Color of glitch lines
    "glitch_min_duration": 50,  # Minimum time glitch stays visible (ms)
    "glitch_max_duration": 150,  # Maximum time glitch stays visible (ms)
    "glitch_trigger_min": 500,  # Minimum interval between glitches (ms)
    "glitch_trigger_max": 2000,  # Maximum interval between glitches (ms)
    
    # Image Processing Settings
    "image_brightness": 0.4,  # 0.0 = black, 1.0 = original, >1.0 = brighter
    "image_contrast": 1.8,  # 1.0 = original, >1.0 = more contrast
    "image_red_boost": 1.3,  # Boost for red channel (applied if > 60)
    "image_green_reduce": 0.7,  # Reduction for green channel
    "image_blue_reduce": 0.7,  # Reduction for blue channel
    
    # Sound/Console Settings
    "enable_console_messages": True,  # Print messages to console
    "play_ominous_message": True,  # Print ominous message to console
    "ominous_frequency": "13Hz",  # Frequency to display in message
    
    # Closing Effects
    "enable_close_effects": True,  # Add visual effects before closing
    "close_effect_color": "#FF0000",  # Color for closing flash
    "close_effect_duration": 0.1,  # Duration of each flash (seconds)
    
    # Safety Settings
    "enable_escape_key": True,  # Allow closing with Escape key
    "enable_timeout": True,  # Close window after duration (False = stay open)
}

# ============================================================================
# END OF CONFIGURATION - DO NOT EDIT BELOW UNLESS YOU KNOW WHAT YOU'RE DOING
# ============================================================================

def load_external_config() -> Optional[Dict[str, Any]]:
    """Try to load configuration from external JSON file."""
    config_paths = [
        os.path.join(os.path.expanduser("~"), ".scary_window_config.json"),
        os.path.join(os.getcwd(), "scary_window_config.json"),
        "scary_window_config.json"
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    external_config = json.load(f)
                    return external_config
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load config from {path}: {e}")
    return None

def merge_configs(base_config: Dict[str, Any], external_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge external config with base config (external overrides base)."""
    merged = base_config.copy()
    
    for key, value in external_config.items():
        if key in merged:
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = merge_configs(merged[key], value)
            else:
                merged[key] = value
        else:
            merged[key] = value
    
    return merged

def validate_config(config: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate configuration values."""
    try:
        # Window size validation
        if not 0 <= config["window_size_percent"] <= 1.0:
            return False, "window_size_percent must be between 0.0 and 1.0"
        
        if config["window_position"] not in ["center", "random", "top-left", "top-right", "bottom-left", "bottom-right"]:
            return False, "window_position must be one of: center, random, top-left, top-right, bottom-left, bottom-right"
        
        # Timing validation
        if config["display_duration_seconds"] < 0:
            return False, "display_duration_seconds must be >= 0"
        
        if config["close_delay_ms"] < 0:
            return False, "close_delay_ms must be >= 0"
        
        # Color validation (simple hex check)
        def is_hex_color(color: str) -> bool:
            return color.startswith('#') and len(color) == 7 and all(c in '0123456789ABCDEFabcdef' for c in color[1:])
        
        for color_key in ["background_color", "glitch_color", "close_effect_color"]:
            if not is_hex_color(config[color_key]):
                return False, f"{color_key} must be a valid hex color (e.g., #FF0000)"
        
        # Image processing validation
        if config["image_brightness"] < 0:
            return False, "image_brightness must be >= 0"
        
        if config["image_contrast"] < 0:
            return False, "image_contrast must be >= 0"
        
        if config["image_red_boost"] < 0:
            return False, "image_red_boost must be >= 0"
        
        if config["image_green_reduce"] < 0:
            return False, "image_green_reduce must be >= 0"
        
        if config["image_blue_reduce"] < 0:
            return False, "image_blue_reduce must be >= 0"
        
        return True, "Configuration valid"
    
    except KeyError as e:
        return False, f"Missing configuration key: {e}"
    except Exception as e:
        return False, f"Configuration validation error: {e}"

def print_config_summary(config: Dict[str, Any]):
    """Print a summary of the current configuration."""
    print("\n" + "=" * 60)
    print("SCARY WINDOW CONFIGURATION SUMMARY")
    print("=" * 60)
    
    print(f"Window: {config['window_size_percent']*100:.0f}% screen, {config['window_position']} position")
    print(f"Duration: {config['display_duration_seconds']} seconds")
    
    effects = []
    if config["enable_flicker"]: effects.append("Flicker")
    if config["enable_eye_effects"]: effects.append("Eyes")
    if config["enable_glitch_effects"]: effects.append("Glitch")
    if config["enable_close_effects"]: effects.append("Close Effects")
    
    print(f"Effects: {', '.join(effects) if effects else 'None'}")
    print(f"Image: {'URL provided' if config['image_url'] else 'Solid color'}")
    print(f"Safety: {'Escape key enabled' if config['enable_escape_key'] else 'Escape disabled'}")
    print("=" * 60)

class ScaryWindow:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.window = tk.Tk()
        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()
        
        # Calculate window size and position
        self.window_width, self.window_height = self._calculate_window_size()
        self.x_position, self.y_position = self._calculate_window_position()
        
        # Setup window
        self._setup_window()
        
    def _calculate_window_size(self) -> Tuple[int, int]:
        """Calculate window dimensions based on configuration."""
        size_percent = self.config["window_size_percent"]
        
        if size_percent == 1.0:  # Full screen
            return self.screen_width, self.screen_height
        elif size_percent == 0.0:  # Small fixed size
            return 400, 300
        else:  # Percentage of screen
            return int(self.screen_width * size_percent), int(self.screen_height * size_percent)
    
    def _calculate_window_position(self) -> Tuple[int, int]:
        """Calculate window position based on configuration."""
        position = self.config["window_position"]
        
        if position == "random":
            max_x = max(0, self.screen_width - self.window_width)
            max_y = max(0, self.screen_height - self.window_height)
            return random.randint(0, max_x), random.randint(0, max_y)
        
        elif position == "center":
            return (self.screen_width - self.window_width) // 2, (self.screen_height - self.window_height) // 2
        
        elif position == "top-left":
            return 0, 0
        
        elif position == "top-right":
            return self.screen_width - self.window_width, 0
        
        elif position == "bottom-left":
            return 0, self.screen_height - self.window_height
        
        elif position == "bottom-right":
            return self.screen_width - self.window_width, self.screen_height - self.window_height
        
        else:  # Default to center
            return (self.screen_width - self.window_width) // 2, (self.screen_height - self.window_height) // 2
    
    def _setup_window(self):
        """Setup window properties."""
        # Set window geometry
        self.window.geometry(f"{self.window_width}x{self.window_height}+{self.x_position}+{self.y_position}")
        
        # Apply window decorations
        if self.config["borderless"]:
            self.window.overrideredirect(True)
        
        # Set background color
        self.window.configure(bg=self.config["background_color"])
        
        # Set always on top
        if self.config["always_on_top"]:
            self.window.attributes('-topmost', True)
        
        # Bind escape key
        if self.config["enable_escape_key"]:
            self.window.bind('<Escape>', lambda event: self._safe_destroy())
    
    def _safe_destroy(self):
        """Safely destroy the window."""
        try:
            self.window.destroy()
        except:
            pass
    
    def load_and_process_image(self):
        """Load and process the image if URL is provided."""
        if not self.config["image_url"]:
            return None
        
        try:
            # Download image
            with urllib.request.urlopen(self.config["image_url"]) as response:
                image_data = response.read()
            
            # Process image
            from PIL import Image, ImageTk, ImageEnhance
            import io
            
            image = Image.open(io.BytesIO(image_data))
            
            # Apply brightness adjustment
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(self.config["image_brightness"])
            
            # Apply contrast adjustment
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.config["image_contrast"])
            
            # Apply color adjustments
            r, g, b = image.split()
            r = r.point(lambda i: i * self.config["image_red_boost"] if i > 60 else i)
            g = g.point(lambda i: i * self.config["image_green_reduce"])
            b = b.point(lambda i: i * self.config["image_blue_reduce"])
            image = Image.merge('RGB', (r, g, b))
            
            # Resize to fit window
            image = image.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            return ImageTk.PhotoImage(image)
        
        except Exception as e:
            if self.config["enable_console_messages"]:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to load image: {e}")
            return None
    
    def flicker_effect(self):
        """Apply flickering effect."""
        if not self.config["enable_flicker"]:
            return
        
        colors = self.config["flicker_colors"]
        self.window.configure(bg=random.choice(colors))
        
        interval = random.randint(
            self.config["flicker_min_interval"],
            self.config["flicker_max_interval"]
        )
        self.window.after(interval, self.flicker_effect)
    
    def add_eye_effect(self, canvas: tk.Canvas):
        """Add eye effect to canvas."""
        for _ in range(self.config["eye_count"]):
            x = random.randint(50, self.window_width - 50)
            y = random.randint(50, self.window_height - 50)
            size = random.randint(self.config["eye_min_size"], self.config["eye_max_size"])
            
            # Draw eye (white part)
            canvas.create_oval(x-size, y-size//2, x+size, y+size//2, 
                              fill='#FFFFFF', outline='', width=0)
            
            # Draw pupil
            pupil_size = size // 3
            canvas.create_oval(x-pupil_size, y-pupil_size//2, 
                              x+pupil_size, y+pupil_size//2, 
                              fill='#000000', outline='', width=0)
            
            # Remove after random duration
            duration = random.randint(
                self.config["eye_min_duration"],
                self.config["eye_max_duration"]
            )
            self.window.after(duration, lambda c=canvas: c.delete('all') if c.winfo_exists() else None)
    
    def trigger_eyes(self):
        """Trigger eye effects at intervals."""
        if not self.config["enable_eye_effects"]:
            return
        
        try:
            canvas = tk.Canvas(self.window, bg='', highlightthickness=0)
            canvas.place(x=0, y=0, width=self.window_width, height=self.window_height)
            self.add_eye_effect(canvas)
        except:
            pass
        
        interval = random.randint(
            self.config["eye_trigger_min"],
            self.config["eye_trigger_max"]
        )
        self.window.after(interval, self.trigger_eyes)
    
    def glitch_effect(self):
        """Apply glitch effect."""
        if not self.config["enable_glitch_effects"]:
            return
        
        try:
            glitch_canvas = tk.Canvas(self.window, bg='', highlightthickness=0)
            glitch_canvas.place(x=0, y=0, width=self.window_width, height=self.window_height)
            
            # Add random glitch lines
            count = random.randint(
                self.config["glitch_min_count"],
                self.config["glitch_max_count"]
            )
            
            for _ in range(count):
                x1 = random.randint(0, self.window_width)
                y1 = random.randint(0, self.window_height)
                width = random.randint(self.config["glitch_width_min"], self.config["glitch_width_max"])
                height = random.randint(self.config["glitch_height_min"], self.config["glitch_height_max"])
                glitch_canvas.create_rectangle(x1, y1, x1+width, y1+height, 
                                              fill=self.config["glitch_color"], outline='', width=0)
            
            # Remove after short duration
            duration = random.randint(
                self.config["glitch_min_duration"],
                self.config["glitch_max_duration"]
            )
            self.window.after(duration, glitch_canvas.destroy if glitch_canvas.winfo_exists() else lambda: None)
        except:
            pass
        
        # Schedule next glitch
        interval = random.randint(
            self.config["glitch_trigger_min"],
            self.config["glitch_trigger_max"]
        )
        self.window.after(interval, self.glitch_effect)
    
    def close_with_effects(self):
        """Close window with optional visual effects."""
        if self.config["enable_close_effects"]:
            try:
                original_color = self.window.cget('bg')
                self.window.configure(bg=self.config["close_effect_color"])
                self.window.update()
                time.sleep(self.config["close_effect_duration"])
                self.window.configure(bg='#000000')
                self.window.update()
                time.sleep(self.config["close_effect_duration"])
            except:
                pass
        
        # Add delay if specified
        if self.config["close_delay_ms"] > 0:
            self.window.after(self.config["close_delay_ms"], self._safe_destroy)
        else:
            self._safe_destroy()
    
    def run(self):
        """Run the scary window application."""
        # Try to load and display image
        photo = self.load_and_process_image()
        
        if photo:
            try:
                image_label = tk.Label(self.window, image=photo, bg="#000000")
                image_label.image = photo  # Keep reference
                image_label.place(x=0, y=0, width=self.window_width, height=self.window_height)
                
                if self.config["enable_console_messages"]:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Image loaded and processed")
            except Exception as e:
                if self.config["enable_console_messages"]:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Failed to display image: {e}")
        
        # Start effects
        if self.config["enable_flicker"]:
            self.flicker_effect()
        
        if self.config["enable_eye_effects"]:
            self.window.after(1000, self.trigger_eyes)
        
        if self.config["enable_glitch_effects"]:
            self.window.after(500, self.glitch_effect)
        
        # Print console messages
        if self.config["enable_console_messages"]:
            current_time = datetime.now().strftime('%H:%M:%S')
            print(f"[{current_time}] [INFO] Scary window activated")
            print(f"[{current_time}] [INFO] Screen size: {self.screen_width}x{self.screen_height}")
            print(f"[{current_time}] [INFO] Window size: {self.window_width}x{self.window_height}")
            
            if self.config["enable_timeout"]:
                print(f"[{current_time}] [INFO] Window will close in {self.config['display_duration_seconds']} seconds")
            
            if self.config["play_ominous_message"]:
                print(f"[{current_time}] [INFO] Playing ominous frequency: {self.config['ominous_frequency']}...")
        
        # Schedule closing
        if self.config["enable_timeout"] and self.config["display_duration_seconds"] > 0:
            close_ms = self.config["display_duration_seconds"] * 1000
            self.window.after(close_ms, self.close_with_effects)
        
        # Run the window
        try:
            self.window.mainloop()
        except:
            pass
        
        if self.config["enable_console_messages"]:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Window deactivated")

def main():
    """Main function."""
    # Load external config if available
    external_config = load_external_config()
    if external_config:
        config = merge_configs(CONFIG, external_config)
        if config["enable_console_messages"]:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Loaded external configuration")
    else:
        config = CONFIG.copy()
    
    # Validate configuration
    is_valid, message = validate_config(config)
    if not is_valid:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Configuration error: {message}")
        print("[ERROR] Using default configuration with minimal settings...")
        # Use safe defaults
        config = {
            "window_size_percent": 0.5,
            "window_position": "center",
            "borderless": True,
            "always_on_top": True,
            "background_color": "#000000",
            "display_duration_seconds": 10,
            "enable_escape_key": True,
            "enable_timeout": True,
            "enable_console_messages": True
        }
    
    # Print configuration summary
    if config["enable_console_messages"]:
        print_config_summary(config)
    
    # Create and run the scary window
    try:
        scary_window = ScaryWindow(config)
        scary_window.run()
    except Exception as e:
        if config["enable_console_messages"]:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Failed to create window: {e}")
    
    sys.exit(0)

if __name__ == "__main__":
    try:
        # Try to import required modules
        try:
            from PIL import Image, ImageTk, ImageEnhance
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Installing Pillow...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "--quiet"])
            from PIL import Image, ImageTk, ImageEnhance
        
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Script interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {e}")
        sys.exit(1)
