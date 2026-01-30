
import tkinter as tk
from tkinter import messagebox
import requests
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw
import sys
import subprocess
from typing import List, Tuple, Optional


class ImageGridDisplay:
    """Improved version of the image display application with better structure and error handling"""
    
    def __init__(self):
        self.root = None
        self.canvas = None
        self.photo = None
        self.image_objects = []
        self.positions = []
        self.screen_width = 0
        self.screen_height = 0
        self.cell_width = 0
        self.cell_height = 0
        
    def check_dependencies(self) -> bool:
        """Check and install required packages"""
        required_packages = ['requests', 'PIL']
        
        for package in required_packages:
            try:
                if package == 'PIL':
                    import PIL
                else:
                    __import__(package)
            except ImportError:
                response = messagebox.askyesno(
                    "Missing Dependencies",
                    f"The '{package}' package is required but not installed.\n"
                    "Would you like to install it now?"
                )
                
                if response:
                    try:
                        subprocess.check_call([
                            sys.executable, "-m", "pip", "install", 
                            "requests" if package == "requests" else "pillow"
                        ])
                        messagebox.showinfo("Success", f"{package} installed successfully!")
                    except subprocess.CalledProcessError:
                        messagebox.showerror(
                            "Installation Failed",
                            f"Failed to install {package}. Please install manually."
                        )
                        return False
                else:
                    return False
        return True
    
    def load_image_from_url(self, url: str) -> Optional[Image.Image]:
        """Load image from URL with error handling"""
        try:
            print(f"Loading image from: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()  # Raise exception for bad status codes
            
            # Verify content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(f"Warning: URL doesn't appear to be an image (Content-Type: {content_type})")
            
            # Load and verify image
            image = Image.open(BytesIO(response.content))
            image.verify()  # Verify it's a valid image
            image = Image.open(BytesIO(response.content))  # Reopen after verify
            
            print(f"Successfully loaded image: {image.width}x{image.height}, Mode: {image.mode}")
            return image
            
        except requests.exceptions.RequestException as e:
            print(f"Network error loading image: {e}")
        except Image.UnidentifiedImageError:
            print("Error: Downloaded content is not a valid image")
        except Exception as e:
            print(f"Unexpected error loading image: {e}")
            
        return None
    
    def create_fallback_image(self, width: int, height: int) -> Image.Image:
        """Create a fallback image when URL loading fails"""
        print("Creating fallback image...")
        image = Image.new('RGBA', (width, height), color=(255, 0, 0, 255))
        draw = ImageDraw.Draw(image)
        
        # Add some text to the fallback image
        try:
            # Try to draw centered text
            from PIL import ImageFont
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            text = "IMAGE\nERROR"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        except:
            # Simple text if font loading fails
            draw.text((10, 10), "IMG", fill=(255, 255, 255, 255))
        
        return image
    
    def calculate_grid_positions(self) -> List[Tuple[int, int]]:
        """Calculate positions for a 10x5 grid (right to left, top to bottom)"""
        positions = []
        for i in range(50):  # 10 columns × 5 rows = 50 positions
            row = i // 10
            col = 9 - (i % 10)  # Right to left order
            x = col * self.cell_width + (self.cell_width // 20)  # Centered in cell
            y = row * self.cell_height + (self.cell_height // 20)
            positions.append((x, y))
        return positions
    
    def setup_window(self) -> None:
        """Configure the main application window"""
        self.root = tk.Tk()
        self.root.title("Image Display")
        
        # Remove window decorations and set to fullscreen
        self.root.overrideredirect(True)
        
        # Get screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Set window to fullscreen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        
        # Configure transparency (if supported by OS)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
            self.root.configure(bg='black')
            print("Transparency enabled")
        except:
            print("Transparency not supported on this platform")
            self.root.configure(bg='black')
        
        # Keep window on top
        self.root.attributes('-topmost', True)
        
        # Escape key to exit
        self.root.bind('<Escape>', lambda e: self.cleanup_and_exit())
        
        # Also exit on Alt+F4 and other common exit methods
        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)
        
    def setup_canvas(self) -> None:
        """Setup canvas for image display"""
        self.canvas = tk.Canvas(
            self.root, 
            width=self.screen_width, 
            height=self.screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)
    
    def prepare_image(self) -> None:
        """Load and prepare the image for display"""
        # Calculate cell size for 10x5 grid
        self.cell_width = self.screen_width // 10
        self.cell_height = self.screen_height // 5
        
        # Image URL (using a reliable placeholder image)
        image_urls = [
            "https://images.unsplash.com/photo-1562860149-691401a306f8?w=400&h=300&fit=crop",
            "https://picsum.photos/400/300",  # Random placeholder
            "https://via.placeholder.com/400x300/FF0000/FFFFFF?text=Image+Display"
        ]
        
        image = None
        for url in image_urls:
            image = self.load_image_from_url(url)
            if image:
                break
        
        # Create fallback if no URL worked
        if not image:
            print("All URL attempts failed, using fallback image")
            image = self.create_fallback_image(
                self.cell_width - 20,
                self.cell_height - 20
            )
        
        # Resize image to fit cell
        target_size = (self.cell_width - 20, self.cell_height - 20)
        if image.size != target_size:
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage for tkinter
        self.photo = ImageTk.PhotoImage(image)
        
        # Calculate grid positions
        self.positions = self.calculate_grid_positions()
    
    def create_next_image(self, index: int = 0) -> None:
        """Create and display the next image in sequence"""
        if index >= 50:
            # All images created, start removal
            self.root.after(500, self.remove_next_image)
            return
        
        # Create image on canvas
        x, y = self.positions[index]
        img_id = self.canvas.create_image(x, y, image=self.photo, anchor='nw')
        self.image_objects.append(img_id)
        
        print(f"Displayed image {index + 1}/50")
        
        # Remove oldest if more than 10 visible
        if len(self.image_objects) > 10:
            old_id = self.image_objects.pop(0)
            self.canvas.delete(old_id)
            print(f"  Removed oldest image ({len(self.image_objects)} visible)")
        
        # Schedule next image
        self.root.after(50, lambda: self.create_next_image(index + 1))
    
    def remove_next_image(self) -> None:
        """Remove images one by one"""
        if not self.image_objects:
            print("\n" + "=" * 50)
            print("PROGRAM COMPLETE")
            print("=" * 50)
            self.root.after(1000, self.cleanup_and_exit)
            return
        
        # Remove next image
        img_id = self.image_objects.pop(0)
        self.canvas.delete(img_id)
        
        remaining = len(self.image_objects)
        if remaining > 0:
            print(f"Removed image ({remaining} remaining)")
            self.root.after(50, self.remove_next_image)
    
    def cleanup_and_exit(self, event=None) -> None:
        """Clean up resources and exit application"""
        print("Cleaning up and exiting...")
        if self.root:
            self.root.destroy()
    
    def run(self) -> None:
        """Main execution method"""
        print("=" * 60)
        print("IMAGE GRID DISPLAY")
        print("=" * 60)
        
        # Check and install dependencies
        if not self.check_dependencies():
            print("Dependencies not met. Exiting.")
            return
        
        try:
            # Setup and run application
            self.setup_window()
            self.setup_canvas()
            self.prepare_image()
            
            # Start image display sequence
            print("\nStarting display in 2 seconds...")
            print("Images will appear from top-right to bottom-left")
            print("Only 10 images visible at a time")
            print("Press ESC to exit at any time")
            print("-" * 60)
            
            self.root.after(2000, lambda: self.create_next_image(0))
            
            # Start main loop
            self.root.mainloop()
            
        except Exception as e:
            print(f"Fatal error: {e}")
            if self.root:
                self.root.destroy()
            raise


def main():
    """Main entry point"""
    try:
        app = ImageGridDisplay()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")


if __name__ == "__main__":
    main()
