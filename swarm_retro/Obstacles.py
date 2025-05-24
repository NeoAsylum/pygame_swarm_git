import random
import pygame
from env import *


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.speed_x = OBSTACLE_SPEED
        # Create the Pygame surface
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((200, 0, 0, 150))  # Red color with slight transparency
        x = SCREEN_WIDTH  # Start at the right edge
        # Spawn at a random vertical position
        y = random.randint(
            0, SCREEN_HEIGHT - OBSTACLE_HEIGHT
        )  # Ensure fully on screen vertically
        # Define the rect for collisions and positioning
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        """Move the obstacle to the left and remove it if it goes off-screen."""
        self.rect.x -= self.speed_x

        # If the right edge of the obstacle is to the left of the screen's left edge (x=0)
        if self.rect.right < 0:
            self.kill()  # Remove this sprite from all groups it belongs to
