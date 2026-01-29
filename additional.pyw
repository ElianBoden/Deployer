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

def display_images_top_right_to_bottom_left(image_url, num_displays=50, delay_seconds=0.05):
    """
    Display images starting from TOP-RIGHT corner, moving left across row, then down.
    
    Args:
        image_url: URL of the image
        num_displays: Total number of images to display (default: 50)
        delay_seconds: Delay between displays (default: 0.05)
    """
    
    # Initialize PyGame
    pygame.init()
    
    # Download the image
    image = download_image_from_url(image_url)
    if image is None:
        print("Failed to download image. Exiting.")
        return
    
    # Get image original size
    image_width, image_height = image.get_size()
    print(f"Displaying {num_displays} copies of the image...")
    
    # Calculate grid dimensions (10 columns x 5 rows for 50 images)
    grid_cols = 10
    grid_rows = 5
    
    # Create window
    screen_width = image_width * grid_cols
    screen_height = image_height * grid_rows
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Image Display - Starting from Top-Right")
    
    # Fill background
    screen.fill((240, 240, 240))
    pygame.display.flip()
    
    # Display images one by one starting from TOP-RIGHT
    images_displayed = 0
    clock = pygame.time.Clock()
    
    running = True
    while running and images_displayed < num_displays:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Pause on space bar
                    paused = True
                    while paused:
                        for e in pygame.event.get():
                            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                                paused = False
                            elif e.type == pygame.QUIT:
                                paused = False
                                running = False
                        clock.tick(10)
        
        # Calculate position STARTING FROM TOP-RIGHT
        row = images_displayed // grid_cols  # Which row (0 = top row)
        col_in_row = images_displayed % grid_cols  # Which column in the current row
        
        # Start from rightmost column and move left
        # For row 0: columns 9, 8, 7, ..., 0
        # For row 1: columns 9, 8, 7, ..., 0
        # etc.
        col = grid_cols - 1 - col_in_row  # This gives us: 9, 8, 7, ..., 0 for each row
        
        x_pos = col * image_width
        y_pos = row * image_height
        
        # Display the image
        screen.blit(image, (x_pos, y_pos))
        
        # Update only the portion where we drew
        pygame.display.update(pygame.Rect(x_pos, y_pos, image_width, image_height))
        
        # Increment counter
        images_displayed += 1
        
        # Show progress
        if images_displayed % 5 == 0:
            print(f"Progress: {images_displayed}/{num_displays} - Position: Row {row+1}, Col {col+1}")
        
        # Delay before next image
        if images_displayed < num_displays:
            time.sleep(delay_seconds)
    
    # Final update
    pygame.display.flip()
    
    # Keep window open
    if running:
        print(f"\n✓ Display complete! {images_displayed} images shown.")
        print("   Starting from TOP-RIGHT, moving left across each row")
        print("   Press ESC or close window to exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            clock.tick(30)
    
    pygame.quit()
    sys.exit()

# Alternative simpler version with clear visualization
def display_images_corner_to_corner():
    """Display images starting from top-right corner to bottom-left corner."""
    
    # Image URL (using your eBay example)
    IMAGE_URL = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    
    print("\n" + "="*60)
    print("IMAGE DISPLAY: TOP-RIGHT → BOTTOM-LEFT")
    print("="*60)
    
    # Initialize
    pygame.init()
    
    # Download image
    try:
        response = requests.get(IMAGE_URL)
        image_data = BytesIO(response.content)
        image = pygame.image.load(image_data)
    except:
        print("Error loading image. Make sure you have internet connection.")
        return
    
    # Image dimensions
    width, height = image.get_size()
    print(f"Image size: {width}x{height}")
    
    # Grid setup (10 columns x 5 rows = 50 images)
    cols, rows = 10, 5
    screen = pygame.display.set_mode((width * cols, height * rows))
    pygame.display.set_caption(f"50 Images - Top-Right to Bottom-Left")
    
    # Background
    screen.fill((230, 230, 230))
    
    # Draw grid lines for visualization
    for c in range(cols + 1):
        pygame.draw.line(screen, (200, 200, 200), 
                        (c * width, 0), (c * width, height * rows), 1)
    for r in range(rows + 1):
        pygame.draw.line(screen, (200, 200, 200),
                        (0, r * height), (width * cols, r * height), 1)
    pygame.display.flip()
    
    print("\nStarting display sequence...")
    print("Top-Right → Moving left across row → Next row → Repeat")
    print("-" * 60)
    
    # Display images one by one
    for i in range(50):
        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Calculate position: Start from top-right (col=9, row=0)
        row = i // cols  # 0, 0, 0, ... (first 10), then 1, 1, 1, ...
        col_in_row = i % cols  # 0, 1, 2, ... 9
        
        # Start from rightmost column (9) and move left
        col = cols - 1 - col_in_row  # 9, 8, 7, ... 0
        
        x = col * width
        y = row * height
        
        # Display image
        screen.blit(image, (x, y))
        
        # Draw a green border around the current image
        pygame.draw.rect(screen, (0, 200, 0), 
                        (x, y, width, height), 3)
        
        pygame.display.update(pygame.Rect(x-5, y-5, width+10, height+10))
        
        # Print current position
        print(f"Image {i+1:2d}: Position (Row {row+1}, Col {col+1}) [X:{x}, Y:{y}]")
        
        # Delay (except for last image)
        if i < 49:
            time.sleep(0.05)
    
    print("-" * 60)
    print("✓ All 50 images displayed!")
    print(f"  Path: Top-Right (Row 1, Col 10) → Bottom-Left (Row 5, Col 1)")
    print("  Window will close in 10 seconds...")
    
    # Keep window open
    time.sleep(10)
    pygame.quit()

# Main execution
if __name__ == "__main__":
    # Install required packages if needed
    try:
        import requests
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pygame"])
        import requests
    
    # Choose which function to run:
    
    # Option 1: Detailed version with controls
    IMAGE_URL = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    # You can change the URL to any image:
    # IMAGE_URL = "https://picsum.photos/200/300"  # Random image
    
    print("\nChoose display option:")
    print("1. Detailed version (with pause/resume controls)")
    print("2. Simple version (automatic, with visualization)")
    
    choice = input("Enter 1 or 2 (default 2): ").strip()
    
    if choice == "1":
        display_images_top_right_to_bottom_left(IMAGE_URL, 50, 0.05)
    else:
        display_images_corner_to_corner()
