
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
        response.raise_for_status()  # Check for HTTP errors
        
        # Create a file-like object from the response content
        image_data = BytesIO(response.content)
        
        # Load the image in PyGame
        image = pygame.image.load(image_data)
        print(f"Image downloaded successfully. Size: {image.get_width()}x{image.get_height()}")
        return image
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return None
    except pygame.error as e:
        print(f"Error loading image data: {e}")
        return None

def display_web_image_repeatedly(image_url, num_displays=50, delay_seconds=0.05):
    """
    Display an image from a URL multiple times in a grid pattern.
    
    Args:
        image_url: URL of the image to download and display
        num_displays: Total number of times to display the image (default: 50)
        delay_seconds: Delay between displays in seconds (default: 0.05)
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
    
    # Calculate grid dimensions (aim for a roughly square arrangement)
    grid_cols = int(num_displays ** 0.5) + 1
    grid_rows = (num_displays + grid_cols - 1) // grid_cols
    
    # Create a window that can fit all images
    screen_width = image_width * grid_cols
    screen_height = image_height * grid_rows
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(f"Image Display - {num_displays} copies")
    
    # Fill background with white
    screen.fill((255, 255, 255))
    pygame.display.flip()  # Initial display
    
    # Display images one by one with delay
    images_displayed = 0
    
    # Main display loop
    running = True
    while running and images_displayed < num_displays:
        # Handle events (allow quitting during display)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Space key to pause/resume
                    paused = True
                    while paused:
                        for e in pygame.event.get():
                            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                                paused = False
                            elif e.type == pygame.QUIT:
                                paused = False
                                running = False
        
        # Calculate position for current image
        row = images_displayed // grid_cols
        col = images_displayed % grid_cols
        x_pos = col * image_width
        y_pos = row * image_height
        
        # Display the image at calculated position
        screen.blit(image, (x_pos, y_pos))
        pygame.display.update(pygame.Rect(x_pos, y_pos, image_width, image_height))
        
        # Increment counter
        images_displayed += 1
        
        # Display progress in console
        if images_displayed % 10 == 0:
            print(f"Progress: {images_displayed}/{num_displays}")
        
        # Delay before next image (if not the last one)
        if images_displayed < num_displays:
            time.sleep(delay_seconds)
    
    # Final update to ensure all images are visible
    pygame.display.flip()
    
    # Keep window open after all images are displayed
    if running:
        print(f"\nDisplay complete! {images_displayed} images shown.")
        print("Press ESC or close window to exit.")
        
        clock = pygame.time.Clock()
        while running:
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

# Simplified version without keeping window open
def quick_display_from_url():
    """Simpler version that closes after displaying all images."""
    
    # Image URL (using the eBay image from your example)
    IMAGE_URL = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    
    print("Starting image display...")
    
    # Initialize PyGame
    pygame.init()
    
    # Download the image
    response = requests.get(IMAGE_URL)
    image_data = BytesIO(response.content)
    image = pygame.image.load(image_data)
    
    # Get image size
    width, height = image.get_size()
    print(f"Image size: {width}x{height}")
    
    # Set up display window (grid of images)
    num_displays = 50
    grid_cols = 10  # 10 columns
    grid_rows = 5   # 5 rows (10x5=50 images)
    
    screen = pygame.display.set_mode((width * grid_cols, height * grid_rows))
    pygame.display.set_caption("50 Image Grid Display")
    
    # Fill background
    screen.fill((245, 245, 245))
    pygame.display.flip()
    
    # Display images one by one
    for i in range(num_displays):
        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Calculate position
        row = i // grid_cols
        col = i % grid_cols
        x = col * width
        y = row * height
        
        # Display the image
        screen.blit(image, (x, y))
        
        # Update only the portion of the screen where the image was placed
        pygame.display.update(pygame.Rect(x, y, width, height))
        
        # Wait 0.05 seconds (unless it's the last image)
        if i < num_displays - 1:
            time.sleep(0.05)
        
        # Print progress every 10 images
        if (i + 1) % 10 == 0:
            print(f"Displayed {i + 1}/50 images")
    
    # Final full screen update
    pygame.display.flip()
    print("Display complete!")
    
    # Keep window open for 5 seconds then close
    time.sleep(5)
    pygame.quit()

if __name__ == "__main__":
    # Install required packages if not already installed
    try:
        import requests
    except ImportError:
        print("Installing required packages...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "pygame"])
        import requests
    
    # Configuration
    IMAGE_URL = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    
    # You can change the URL to any image you want
    # IMAGE_URL = "https://example.com/your-image.jpg"
    
    NUM_DISPLAYS = 50
    DELAY_SECONDS = 0.05
    
    print("=" * 60)
    print("WEB IMAGE DISPLAY PROGRAM")
    print("=" * 60)
    print(f"Image URL: {IMAGE_URL}")
    print(f"Number of displays: {NUM_DISPLAYS}")
    print(f"Delay between displays: {DELAY_SECONDS} seconds")
    print("-" * 60)
    
    # Run the main display function
    display_web_image_repeatedly(IMAGE_URL, NUM_DISPLAYS, DELAY_SECONDS)
    
    # Alternatively, run the simpler version:
    # quick_display_from_url()
