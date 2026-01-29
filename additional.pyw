import pygame
import sys
import time
import requests
from io import BytesIO

def download_image_from_url(image_url):
    """Download image from URL and return a PyGame surface."""
    try:
        print(f"Downloading image from: {image_url}")
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        image_data = BytesIO(response.content)
        image = pygame.image.load(image_data)
        print(f"Image downloaded successfully. Size: {image.get_width()}x{image.get_height()}")
        return image
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
    except pygame.error as e:
        print(f"Error loading image data: {e}")
        return None

def display_images_top_right_to_bottom_left():
    """
    Display 50 images starting from TOP-RIGHT corner, moving left across row, then down.
    No user input required - runs automatically.
    """
    
    # Image URL (using the eBay image from your example)
    IMAGE_URL = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    
    print("=" * 60)
    print("DISPLAYING 50 IMAGES FROM TOP-RIGHT TO BOTTOM-LEFT")
    print("=" * 60)
    
    # Initialize PyGame
    pygame.init()
    
    # Download the image
    image = download_image_from_url(IMAGE_URL)
    if image is None:
        print("Failed to download image. Exiting.")
        return
    
    # Get image original size
    image_width, image_height = image.get_size()
    num_displays = 50
    delay_seconds = 0.05
    
    print(f"Displaying {num_displays} copies of the image...")
    print(f"Delay between images: {delay_seconds} seconds")
    print(f"Path: Top-Right → Moving left → Next row → Repeat")
    print("-" * 60)
    
    # Calculate grid dimensions (10 columns x 5 rows for 50 images)
    grid_cols = 10
    grid_rows = 5
    
    # Create window
    screen_width = image_width * grid_cols
    screen_height = image_height * grid_rows
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("50 Images - Top-Right to Bottom-Left")
    
    # Fill background
    screen.fill((240, 240, 240))
    pygame.display.flip()
    
    # Display images one by one starting from TOP-RIGHT
    images_displayed = 0
    clock = pygame.time.Clock()
    
    running = True
    while running and images_displayed < num_displays:
        # Handle events (allow quitting during display)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Calculate position STARTING FROM TOP-RIGHT
        row = images_displayed // grid_cols  # Which row (0 = top row)
        col_in_row = images_displayed % grid_cols  # Which column in the current row
        
        # Start from rightmost column and move left
        col = grid_cols - 1 - col_in_row  # This gives us: 9, 8, 7, ..., 0 for each row
        
        x_pos = col * image_width
        y_pos = row * image_height
        
        # Display the image
        screen.blit(image, (x_pos, y_pos))
        
        # Update only the portion where we drew
        pygame.display.update(pygame.Rect(x_pos, y_pos, image_width, image_height))
        
        # Increment counter
        images_displayed += 1
        
        # Show progress every 5 images
        if images_displayed % 5 == 0 or images_displayed == num_displays:
            print(f"Progress: {images_displayed}/{num_displays} - Position: Row {row+1}, Column {col+1}")
        
        # Delay before next image (if not the last one)
        if images_displayed < num_displays:
            time.sleep(delay_seconds)
    
    # Final update
    pygame.display.flip()
    
    # Keep window open for a while after completion
    print("-" * 60)
    print(f"✓ Display complete! {images_displayed} images shown.")
    print("  Window will remain open for 30 seconds.")
    print("  Press ESC or close window to exit earlier.")
    
    # Keep window open for 30 seconds or until user closes it
    start_time = time.time()
    while running and time.time() - start_time < 30:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Limit frame rate to reduce CPU usage
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

def quick_simple_display():
    """Even simpler version - minimal code, no extra features."""
    
    # Image URL
    IMAGE_URL = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    
    print("Starting simple image display...")
    
    try:
        # Initialize and download
        pygame.init()
        
        # Download image
        response = requests.get(IMAGE_URL)
        image_data = BytesIO(response.content)
        image = pygame.image.load(image_data)
        
        # Get size
        width, height = image.get_size()
        
        # Setup grid
        cols, rows = 10, 5
        screen = pygame.display.set_mode((width * cols, height * rows))
        screen.fill((255, 255, 255))
        
        print(f"Displaying 50 images ({width}x{height} each)")
        print("Starting from top-right, moving left...")
        
        # Display loop
        for i in range(50):
            # Check for quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Calculate position (top-right to bottom-left)
            row = i // cols
            col_in_row = i % cols
            col = cols - 1 - col_in_row  # Start from rightmost
            
            x = col * width
            y = row * height
            
            # Draw image
            screen.blit(image, (x, y))
            pygame.display.update(pygame.Rect(x, y, width, height))
            
            # Delay
            if i < 49:
                time.sleep(0.05)
        
        print("Display complete!")
        
        # Keep window open briefly
        time.sleep(5)
        pygame.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()

# Main execution - automatically runs without asking for input
if __name__ == "__main__":
    # Try to install required packages if needed
    try:
        import requests
    except ImportError:
        print("Required packages not found. Trying to install...")
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pygame"])
            print("Packages installed successfully!")
            import requests
            import pygame
        except:
            print("Failed to install packages. Please install manually:")
            print("pip install requests pygame")
            sys.exit(1)
    
    # Run the display - choose one of these:
    
    # Option 1: Full featured version (recommended)
    display_images_top_right_to_bottom_left()
    
    # Option 2: Minimal version (if the above has issues)
    # quick_simple_display()
