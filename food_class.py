import pygame
from env import FOOD_SIZE


class Food(pygame.sprite.Sprite):
    """
    Represents a food item in the game.
    Food items are simple circles that can be consumed by other game entities.
    """
    def __init__(self, x, y):
        """
        Initializes a new food item.

        Args:
            x (int): The x-coordinate for the food item's position.
            y (int): The y-coordinate for the food item's position.
        """
        super().__init__()
        self.x = x
        self.y = y
        self.width = FOOD_SIZE
        self.height = FOOD_SIZE
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, 
                           (220, 50, 50, 200),
                           (self.width // 2, self.height // 2), self.width // 2)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        """
        Draws the food item on the given screen.

        Args:
            screen (pygame.Surface): The Pygame surface to draw the food item on.
        """
        screen.blit(self.image, self.rect)
