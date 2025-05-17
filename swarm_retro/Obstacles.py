# This should be in your Obstacles.py file or at the top of your main script
import pygame
import random # Not strictly needed in this class file, but often useful

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed): # Added speed parameter
        super().__init__()  # Initialize as a Pygame Sprite
        # self.x and self.y are implicitly handled by self.rect.topleft
        self.width = width
        self.height = height
        self.speed_x = speed # Speed at which obstacle moves to the left

        # Create the Pygame surface
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((200, 0, 0, 150))  # Red color with slight transparency

        # Define the rect for collisions and positioning
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        """Move the obstacle to the left and remove it if it goes off-screen."""
        self.rect.x -= self.speed_x
        
        # If the right edge of the obstacle is to the left of the screen's left edge (x=0)
        if self.rect.right < 0:
            self.kill() # Remove this sprite from all groups it belongs to