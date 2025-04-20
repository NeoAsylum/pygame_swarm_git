import pygame

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()  # Initialize as a Pygame Sprite
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Create the Pygame surface
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((200, 0, 0, 150))  # Red color with slight transparency

        # Define the rect for collisions
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)  # Draw obstacle onto the screen
