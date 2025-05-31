import random
import pygame

from env import *

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed_x = OBSTACLE_SPEED

        # 1. Create the comet head image using the new color scheme
        self.head_image_orig = self._create_comet_head_surface() # Store original for potential reuse
        self.head_image = self.head_image_orig.copy() # Use a copy
        self.head_width = self.head_image.get_width()
        self.head_height = self.head_image.get_height()

        # 2. Initialize trail properties
        self.trail_particles = []
        self.frames_since_last_spawn = 0

        # 3. Create the main sprite image (head + area for trail)
        self.image_width = self.head_width + COMET_TRAIL_RENDER_WIDTH
        self.image_height = self.head_height # Or make slightly taller if trail spreads
        self.image = pygame.Surface((self.image_width, self.image_height), pygame.SRCALPHA)

        # 4. Position the comet
        y_spawn = random.randint(0, SCREEN_HEIGHT - self.image_height)
        # self.rect is for the entire surface (head + trail area)
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, y_spawn))

        # 5. Hitbox for more precise head collision
        # This rect represents the actual head portion of the comet.
        self.hitbox = pygame.Rect(self.rect.left, self.rect.top, self.head_width, self.head_height)

        # Initial drawing of the comet onto its surface
        self._redraw_comet_surface()

    def _create_comet_head_surface(self):
        """Creates a surface for the comet's head with the defined color scheme."""
        head_surface = pygame.Surface((COMET_HEAD_WIDTH, COMET_HEAD_HEIGHT), pygame.SRCALPHA)
        center_x = COMET_HEAD_WIDTH // 2
        center_y = COMET_HEAD_HEIGHT // 2

        # Glow (larger, semi-transparent red circle)
        pygame.draw.circle(head_surface, COMET_HEAD_GLOW_COLOR, (center_x, center_y), COMET_HEAD_WIDTH // 2)

        # Core (smaller, dark red/black circle on top)
        core_radius = int(COMET_HEAD_WIDTH * 0.35)
        pygame.draw.circle(head_surface, COMET_HEAD_CORE_COLOR, (center_x, center_y), core_radius)
        
        return head_surface

    def _redraw_comet_surface(self):
        """Clears and redraws the entire comet (head + trail) onto self.image."""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        # Draw trail particles
        for particle in self.trail_particles:
            pos_x, pos_y = particle['pos']
            radius = particle['radius']
            alpha = particle['alpha']

            if radius > 0 and alpha > 0:
                temp_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                # Use the new COMET_TRAIL_PARTICLE_COLOR
                pygame.draw.circle(temp_surface, (*COMET_TRAIL_PARTICLE_COLOR, int(alpha)),
                                   (radius, radius), radius)
                self.image.blit(temp_surface, (pos_x - radius, pos_y - radius))

        # Draw the head at the left edge of self.image
        self.image.blit(self.head_image, (0, 0))


    def update(self):
        """Move the comet, update its trail, hitbox, and redraw its surface."""
        # 1. Move the entire comet sprite (and its rect)
        self.rect.x -= self.speed_x

        # 2. Update the hitbox position to follow the head
        self.hitbox.topleft = (self.rect.left, self.rect.top)

        # 3. Kill if off-screen (based on the wider self.rect)
        if self.rect.right < 0:
            self.kill()
            return

        # 4. Update trail particles
        new_trail_particles = []
        for particle in self.trail_particles:
            particle['pos'][0] += self.speed_x
            particle['radius'] -= COMET_PARTICLE_RADIUS_DECAY
            particle['alpha'] -= COMET_PARTICLE_ALPHA_DECAY

            if particle['radius'] > 0 and particle['alpha'] > 0 and particle['pos'][0] < self.image_width:
                new_trail_particles.append(particle)
        self.trail_particles = new_trail_particles

        # 5. Spawn new particles
        self.frames_since_last_spawn += 1
        if self.frames_since_last_spawn >= COMET_TRAIL_SPAWN_INTERVAL:
            self.frames_since_last_spawn = 0
            if len(self.trail_particles) < COMET_TRAIL_MAX_PARTICLES:
                spawn_x_on_surface = self.head_width * 0.7 # Start trail from near the back of the head
                spawn_y_on_surface = self.head_height / 2
                self.trail_particles.append({
                    'pos': [spawn_x_on_surface, spawn_y_on_surface],
                    'radius': COMET_PARTICLE_INITIAL_RADIUS,
                    'alpha': COMET_PARTICLE_INITIAL_ALPHA
                })

        # 6. Redraw the entire comet surface
        self._redraw_comet_surface()