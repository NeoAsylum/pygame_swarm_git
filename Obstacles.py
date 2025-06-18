import random
import pygame

from env import *


class Obstacle(pygame.sprite.Sprite):
    """
    Represents a comet-like obstacle that moves across the screen.
    It has a distinct head and a trailing particle effect.
    """

    def __init__(self, speed_x=OBSTACLE_SPEED):
        """
        Initializes the obstacle.

        Args:
            speed_x (float, optional): The horizontal speed of the obstacle.
                                       Defaults to OBSTACLE_SPEED from ENV.py.
        """
        super().__init__()
        self.speed_x = random.uniform(0.8, 1.2) * speed_x
        self.head_image_orig = self._create_comet_head_surface()
        self.head_image = self.head_image_orig.copy()
        self.head_width = self.head_image.get_width()
        self.head_height = self.head_image.get_height()

        self.trail_particles = []
        self.frames_since_last_spawn = 0

        self.image_width = self.head_width  # Image is now just the head
        self.image_height = self.head_height
        self.image = pygame.Surface(
            (self.image_width, self.image_height), pygame.SRCALPHA
        )

        y_spawn = random.randint(0, SCREEN_HEIGHT - self.image_height)
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, y_spawn))
        self.x: float = SCREEN_WIDTH
        self.hitbox = pygame.Rect(
            0, 0, self.head_width, self.head_height
        )  # Hitbox relative to self.rect.topleft

        self._redraw_comet_surface()

    def _create_comet_head_surface(self):
        """
        Creates the visual surface for the comet's head.

        Returns:
            pygame.Surface: A surface representing the comet's head with a glow and core.
        """
        head_surface = pygame.Surface(
            (COMET_HEAD_WIDTH, COMET_HEAD_HEIGHT), pygame.SRCALPHA
        )
        center_x = COMET_HEAD_WIDTH // 2
        center_y = COMET_HEAD_HEIGHT // 2

        pygame.draw.circle(
            head_surface,
            COMET_HEAD_GLOW_COLOR,
            (center_x, center_y),
            COMET_HEAD_WIDTH // 2,
        )

        core_radius = int(COMET_HEAD_WIDTH * 0.35)
        pygame.draw.circle(
            head_surface, COMET_HEAD_CORE_COLOR, (center_x, center_y), core_radius
        )

        return head_surface

    def _redraw_comet_surface(self):
        """
        Redraws the main image surface of the obstacle, typically just the head.
        This is called when the obstacle's appearance might need to be updated.
        """
        self.image.fill((0, 0, 0, 0))
        self.image.blit(self.head_image, (0, 0))

    def update(self):
        """
        Updates the obstacle's position, manages its trail particles, and handles its lifecycle.
        Moves the obstacle horizontally, updates particle decay, spawns new particles,
        and removes the obstacle if it moves off-screen.
        """
        self.x -= self.speed_x
        self.rect.x = int(self.x)

        self.hitbox.topleft = (self.rect.left, self.rect.top)

        if self.rect.right < 0:
            self.kill()
            return

        new_trail_particles = []
        for particle in self.trail_particles:
            # Particles use their own decay rates and do not move with the comet
            particle["radius"] -= particle["radius_decay"]
            particle["alpha"] -= particle["alpha_decay"]

            if particle["radius"] > 0 and particle["alpha"] > 0:
                new_trail_particles.append(particle)
        self.trail_particles = new_trail_particles

        self.frames_since_last_spawn += 1
        if self.frames_since_last_spawn >= COMET_TRAIL_SPAWN_INTERVAL:
            self.frames_since_last_spawn = 0
            if len(self.trail_particles) < COMET_TRAIL_MAX_PARTICLES:
                # Spawn particles at the right edge of the comet's head (world coordinates)
                spawn_world_x = self.rect.right - (self.head_width * 0.2)
                spawn_world_y = self.rect.centery

                # Decide particle type
                if random.random() < COMET_YELLOW_PARTICLE_SPAWN_CHANCE:
                    # Spawn a yellow particle
                    self.trail_particles.append(
                        {
                            "world_pos": [
                                spawn_world_x + random.uniform(-15, 15),
                                spawn_world_y + random.uniform(-15, 15),
                            ],  # Increased random distribution
                            "radius": COMET_YELLOW_PARTICLE_INITIAL_RADIUS,
                            "alpha": COMET_YELLOW_PARTICLE_INITIAL_ALPHA,
                            "color": COMET_TRAIL_YELLOW_PARTICLE_COLOR,
                            "radius_decay": COMET_YELLOW_PARTICLE_RADIUS_DECAY,
                            "alpha_decay": COMET_YELLOW_PARTICLE_ALPHA_DECAY,
                        }
                    )
                else:
                    # Spawn a standard red/orange particle
                    self.trail_particles.append(
                        {
                            "world_pos": [spawn_world_x, spawn_world_y],
                            "radius": COMET_PARTICLE_INITIAL_RADIUS,
                            "alpha": COMET_PARTICLE_INITIAL_ALPHA,
                            "color": COMET_TRAIL_PARTICLE_COLOR,
                            "radius_decay": COMET_PARTICLE_RADIUS_DECAY,
                            "alpha_decay": COMET_PARTICLE_ALPHA_DECAY,
                        }
                    )
        self._redraw_comet_surface()

    def draw_trail_particles(self, surface):
        """
        Draws the trail particles onto the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the particles on.
        """
        for particle in self.trail_particles:
            pos_x, pos_y = particle["world_pos"]
            radius = particle["radius"]
            alpha = particle["alpha"]
            color = particle["color"]

            if radius > 0 and alpha > 0:  # Ensure it's visible
                temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    temp_surface, (*color, int(alpha)), (radius, radius), radius
                )
                surface.blit(temp_surface, (pos_x - radius, pos_y - radius))
