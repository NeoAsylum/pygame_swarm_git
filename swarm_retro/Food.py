# pygame_swarm_git/swarm_retro/Food.py
import pygame
import random
from config_retro import GREEN, FOOD_SIZE, FOOD_ENERGY_VALUE

class Food(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x # Position kann als float für interne Logik bleiben, rect ist für Darstellung/Kollision
        self.y = y
        self.energy_value = FOOD_ENERGY_VALUE
        self.image = pygame.Surface([FOOD_SIZE * 2, FOOD_SIZE * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (FOOD_SIZE, FOOD_SIZE), FOOD_SIZE)
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))
        # Optional: Maske für Food, wenn pixelgenaue Kollision mit Food gewünscht wäre
        # self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen): # Normalerweise nicht nötig, wenn in all_sprites.draw() enthalten
        screen.blit(self.image, self.rect)