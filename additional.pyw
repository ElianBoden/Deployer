import pygame
import sys
import time
import requests
from io import BytesIO

try:
    # Setup
    pygame.init()
    
    # Download image
    url = "https://i.ebayimg.com/images/g/NPAAAOSwP79cdw6P/s-l400.jpg"
    response = requests.get(url)
    image = pygame.image.load(BytesIO(response.content))
    
    # Get size
    width, height = image.get_size()
    
    # Create window (10x5 grid)
    screen = pygame.display.set_mode((width * 10, height * 5))
    screen.fill((255, 255, 255))
    pygame.display.flip()
    
    # Display 50 images starting from top-right
    for i in range(50):
        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Calculate position (top-right to bottom-left)
        row = i // 10  # 0 to 4
        col_in_row = i % 10  # 0 to 9
        col = 9 - col_in_row  # Start from column 9 (rightmost)
        
        x = col * width
        y = row * height
        
        # Draw image
        screen.blit(image, (x, y))
        pygame.display.update(pygame.Rect(x, y, width, height))
        
        # 0.05 second delay between images
        if i < 49:
            time.sleep(0.05)
    
    # Keep window open
    time.sleep(5)
    pygame.quit()
    
except Exception as e:
    print(f"Error: {e}")
    print("Make sure to install: pip install pygame requests")
