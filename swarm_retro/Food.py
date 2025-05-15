# pygame_swarm_git/swarm_retro/Food.py
import pygame
import random
from config_retro import GREEN, FOOD_SIZE, FOOD_ENERGY_VALUE

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.energy_value = FOOD_ENERGY_VALUE
        self.image = pygame.Surface([FOOD_SIZE * 2, FOOD_SIZE * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (FOOD_SIZE, FOOD_SIZE), FOOD_SIZE)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, screen): # Though all_sprites.draw will handle it
        screen.blit(self.image, self.rect)