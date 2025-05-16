# pygame_swarm_git/swarm_retro/Obstacles.py
import pygame
import random
from config_retro import RED, COMET_SIZE_W, COMET_SIZE_H, COMET_MIN_SPEED, COMET_MAX_SPEED, WIDTH, HEIGHT

class CometObstacle(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None, width_val=COMET_SIZE_W, height_val=COMET_SIZE_H, color=RED, auto_spawn_from_edge=True):
        super().__init__()
        self.image = pygame.Surface((width_val, height_val))
        self.image.fill(color)
        self.mask = pygame.mask.from_surface(self.image)

        # Positionen als float für genauere Berechnungen
        self.current_x = 0.0
        self.current_y = 0.0
        self.speed_x = 0.0
        self.speed_y = 0.0

        if auto_spawn_from_edge and x is None and y is None:
            edge = random.choice(["top", "bottom", "left", "right"])
            padding = max(width_val, height_val) + 5

            if edge == "top":
                self.current_x = float(random.randint(0, WIDTH - width_val))
                self.current_y = float(-padding)
                self.speed_x = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
                self.speed_y = random.uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)
            elif edge == "bottom":
                self.current_x = float(random.randint(0, WIDTH - width_val))
                self.current_y = float(HEIGHT + padding)
                self.speed_x = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
                self.speed_y = random.uniform(-COMET_MAX_SPEED, -COMET_MIN_SPEED)
            elif edge == "left":
                self.current_x = float(-padding)
                self.current_y = float(random.randint(0, HEIGHT - height_val))
                self.speed_x = random.uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)
                self.speed_y = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
            else: # "right"
                self.current_x = float(WIDTH + padding)
                self.current_y = float(random.randint(0, HEIGHT - height_val))
                self.speed_x = random.uniform(-COMET_MAX_SPEED, -COMET_MIN_SPEED)
                self.speed_y = random.uniform(-COMET_MAX_SPEED / 2, COMET_MAX_SPEED / 2)
            self.rect = self.image.get_rect(topleft=(round(self.current_x), round(self.current_y)))
        else:
            self.current_x = float(x if x is not None else random.randint(0, WIDTH - width_val))
            self.current_y = float(y if y is not None else -height_val)
            self.rect = self.image.get_rect(topleft=(round(self.current_x), round(self.current_y)))
            self.speed_x = random.uniform(-COMET_MAX_SPEED, COMET_MAX_SPEED)
            self.speed_y = random.uniform(COMET_MIN_SPEED, COMET_MAX_SPEED)

    def update(self):
        self.current_x += self.speed_x
        self.current_y += self.speed_y
        self.rect.topleft = (round(self.current_x), round(self.current_y))

        screen_buffer = 100
        if self.rect.top > HEIGHT + screen_buffer or \
           self.rect.bottom < -screen_buffer or \
           self.rect.left > WIDTH + screen_buffer or \
           self.rect.right < -screen_buffer:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)