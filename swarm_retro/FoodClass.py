import pygame
from env import FOOD_SIZE


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.width = FOOD_SIZE
        self.height = FOOD_SIZE

        # Create the Pygame surface
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((50, 140, 90, 150))

        # Define the rect for collisions
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
