import pygame
from ENV import FOOD_SIZE


class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
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
        screen.blit(self.image, self.rect)
