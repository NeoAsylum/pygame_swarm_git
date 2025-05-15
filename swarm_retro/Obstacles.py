# pygame_swarm_git/swarm_retro/Obstacles.py
import pygame
import random
from config_retro import RED, COMET_SIZE_W, COMET_SIZE_H, COMET_MIN_SPEED, COMET_MAX_SPEED, WIDTH, HEIGHT

class CometObstacle(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None, width_val=COMET_SIZE_W, height_val=COMET_SIZE_H, color=RED, auto_spawn_from_edge=True):
        super().__init__()
        self.image = pygame.Surface((width_val, height_val))
        self.image.fill(color)
        self.mask = pygame.mask.from_surface(self.image) # Hinzugefügt für pixelgenaue Kollision

        if auto_spawn_from_edge and x is None and y is None: # Nur wenn keine Position explizit übergeben wird
            edge = random.choice(["top", "bottom", "left", "right"])
            padding = max(width_val, height_val) + 5 # Ensure it's fully off-screen

            if edge == "top":
                self.current_x = random.randint(0, WIDTH - width_val)
                self.current_y = -padding
                self.speed_x = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
                self.speed_y = random.uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)
            elif edge == "bottom":
                self.current_x = random.randint(0, WIDTH - width_val)
                self.current_y = HEIGHT + padding
                self.speed_x = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
                self.speed_y = random.uniform(-COMET_MAX_SPEED, -COMET_MIN_SPEED)
            elif edge == "left":
                self.current_x = -padding
                self.current_y = random.randint(0, HEIGHT - height_val)
                self.speed_x = random.uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)
                self.speed_y = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
            else: # "right"
                self.current_x = WIDTH + padding
                self.current_y = random.randint(0, HEIGHT - height_val)
                self.speed_x = random.uniform(-COMET_MAX_SPEED, -COMET_MIN_SPEED)
                self.speed_y = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
            self.rect = self.image.get_rect(topleft=(self.current_x, self.current_y))
        else:
            # Manual spawn (e.g., mouse click), x and y are provided or auto_spawn_from_edge is False
            self.current_x = x if x is not None else random.randint(0, WIDTH - width_val)
            self.current_y = y if y is not None else -height_val # Default to top if y is None
            self.rect = self.image.get_rect(topleft=(self.current_x, self.current_y))
            # Default speeds if not overridden after manual spawn
            self.speed_x = random.uniform(-COMET_MAX_SPEED, COMET_MAX_SPEED)
            self.speed_y = random.uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)


    def update(self):
        self.current_x += self.speed_x
        self.current_y += self.speed_y
        self.rect.topleft = (self.current_x, self.current_y)


        # Boundary check: Remove if it goes well off screen after passing through
        screen_buffer = 100 # Increased buffer for removal
        if self.rect.top > HEIGHT + screen_buffer or \
           self.rect.bottom < -screen_buffer or \
           self.rect.left > WIDTH + screen_buffer or \
           self.rect.right < -screen_buffer:
            self.kill()

    def draw(self, screen): # Though all_sprites.draw will handle it
        screen.blit(self.image, self.rect)