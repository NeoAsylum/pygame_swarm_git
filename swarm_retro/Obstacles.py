import random
import pygame

# These are imported from your env.py as per your structure
from env import OBSTACLE_SPEED, SCREEN_HEIGHT, SCREEN_WIDTH
# If other constants from env.py were needed by Obstacle, they'd be imported here too.

# --- Comet Appearance Parameters (Defaults for Black/Red Theme) ---
# These use getattr to allow them to be overridden if defined globally (e.g. in env.py and imported)
# If not defined globally, these default values will be used.

# Head Colors: Dark core with a fiery red glow
COMET_HEAD_WIDTH = getattr(__builtins__, 'COMET_HEAD_WIDTH', 35)
COMET_HEAD_HEIGHT = getattr(__builtins__, 'COMET_HEAD_HEIGHT', 35)
COMET_HEAD_CORE_COLOR = getattr(__builtins__, 'COMET_HEAD_CORE_COLOR', (40, 0, 0, 255))      # Dark, almost black-red core
COMET_HEAD_GLOW_COLOR = getattr(__builtins__, 'COMET_HEAD_GLOW_COLOR', (200, 0, 0, 120))     # Semi-transparent fiery red glow

# Trail Colors & Properties: Fiery red particles
COMET_TRAIL_MAX_PARTICLES = getattr(__builtins__, 'COMET_TRAIL_MAX_PARTICLES', 25)
COMET_TRAIL_SPAWN_INTERVAL = getattr(__builtins__, 'COMET_TRAIL_SPAWN_INTERVAL', 1)
COMET_TRAIL_RENDER_WIDTH = getattr(__builtins__, 'COMET_TRAIL_RENDER_WIDTH', 150)
COMET_TRAIL_PARTICLE_COLOR = getattr(__builtins__, 'COMET_TRAIL_PARTICLE_COLOR', (230, 40, 0)) # Fiery red/orange trail

# Particle Physics
COMET_PARTICLE_INITIAL_RADIUS = getattr(__builtins__, 'COMET_PARTICLE_INITIAL_RADIUS', 8)
COMET_PARTICLE_RADIUS_DECAY = getattr(__builtins__, 'COMET_PARTICLE_RADIUS_DECAY', 0.25)
COMET_PARTICLE_INITIAL_ALPHA = getattr(__builtins__, 'COMET_PARTICLE_INITIAL_ALPHA', 200)
COMET_PARTICLE_ALPHA_DECAY = getattr(__builtins__, 'COMET_PARTICLE_ALPHA_DECAY', 10)
# --- End Comet Parameters ---

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
        # The head is drawn at (0,0) relative to self.image, which is at self.rect.topleft
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

# --- How to use and notes on collision ---
#
# Your env.py should define:
# SCREEN_WIDTH = 1200
# SCREEN_HEIGHT = 700
# OBSTACLE_SPEED = 5
# (And other constants you use elsewhere)
#
# The COMET_... constants above can also be moved to your env.py if you want to centralize them.
# If they are in env.py, ensure they are imported here or that your main game script makes them globally available
# before Obstacle instances are created. The getattr approach provides a fallback if they are not found globally.
#
# Collision Detection:
# - `self.rect`: This is the rectangle for the *entire sprite image*, which includes the head
#   and the transparent area where the trail is rendered. Pygame's default sprite collision
#   functions (like `pygame.sprite.spritecollide` with `dokill=False`) will use this `self.rect`.
#   This means collisions can trigger even if only the transparent part of the trail area overlaps.
#   This is "working" as far as Pygame is concerned.
#
# - `self.hitbox`: This new rectangle is specifically sized and positioned to cover only the
#   comet's head. For more accurate gameplay collisions (e.g., player only collides with the
#   solid part of the comet), you should use `self.hitbox` in your collision checks.
#
#   Example of checking collision with the hitbox:
#   ```python
#   # In your game loop or collision handling function:
#   # Assuming 'player_sprite' is your player
#   # and 'obstacles_group' is a pygame.sprite.Group() of these Obstacle instances.
#
#   for comet in obstacles_group:
#       if player_sprite.rect.colliderect(comet.hitbox):
#           print("Player collided with the head of a comet!")
#           # Handle collision (e.g., game over, lose life)
#           # if you want the comet to disappear on head collision:
#           # comet.kill()
#   ```
#
# The rest of your game logic (spawning obstacles, adding to groups, etc.) should work as before.
#
# --- Example Usage (similar to before, for testing) ---
if __name__ == '__main__':
    # Ensure necessary constants from env.py are "faked" for standalone test
    # In your actual game, these would be imported from your env.py
    # SCREEN_WIDTH = 1200 (already faked by getattr if not defined)
    # SCREEN_HEIGHT = 700
    # OBSTACLE_SPEED = 5

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Black/Red Comet Test")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    
    def spawn_comet():
        comet = Obstacle()
        all_sprites.add(comet)

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 1500) # Spawn a new comet

    spawn_comet()

    # Dummy player for hitbox collision test
    player = pygame.sprite.Sprite()
    player.image = pygame.Surface((30,30))
    player.image.fill((0,255,0)) # Green
    player.rect = player.image.get_rect(center=(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2))


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == SPAWN_EVENT:
                spawn_comet()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # Test spawning
                    spawn_comet()
        
        # Simple player movement for testing collision
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]: player.rect.y -= 5
        if keys[pygame.K_DOWN]: player.rect.y += 5
        if keys[pygame.K_LEFT]: player.rect.x -= 5
        if keys[pygame.K_RIGHT]: player.rect.x += 5
        player.rect.clamp_ip(screen.get_rect())


        all_sprites.update()

        # Collision check using hitbox
        for comet in all_sprites:
            if player.rect.colliderect(comet.hitbox): # Use comet.hitbox here
                print(f"HIT DETECTED with comet head at {comet.hitbox.topleft} by player at {player.rect.topleft}")
                # comet.kill() # Example: destroy comet on head collision
                player.image.fill((255,255,0)) # Yellow on hit
            else:
                player.image.fill((0,255,0)) # Green


        screen.fill((10, 0, 10))  # Dark purple/black background
        all_sprites.draw(screen)
        screen.blit(player.image, player.rect) # Draw dummy player
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()