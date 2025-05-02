# In your main game file (e.g., dudes.py)

# Removed: from pickle import TUPLE (Seems like an error)
import pygame
import random
import sys # Import sys for exiting

# Import your classes
from CometClass import CometObject
from DudeClass import DudeObject
from ExplosionClass import ExplosionObject
from ShoutMessage import ShoutMessage

# Import necessary constants from config
from config import (BLACK, BLUE, COMET_SIZE, COMET_SPAWN_RATE, DUDE_COUNT,
                    DUDE_HEARING_RADIUS, DUDE_HORIZONTAL_VISION_RANGE,
                    DUDE_SEPARATION_RADIUS,
                    EXPLOSION_RADIUS, FPS, GREEN, ORANGE, RED, SCREEN_HEIGHT,
                    SCREEN_WIDTH, DUDE_SIZE, SHOUT_ARROW_COLOR,
                    SHOUT_ARROW_SIZE, SHOUT_CHECK_RADIUS, YELLOW,
                    # Add any other constants needed
                   )

# --- Define Colors if not imported from config ---
WHITE = (255, 255, 255)
PURPLE = (128, 0, 128) # Define Purple since it wasn't imported
CYAN = (0, 255, 255) # Define Cyan (used in visualization)

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
dudes_group = pygame.sprite.Group()
comets_group = pygame.sprite.Group()
explosions_group = pygame.sprite.Group()
shout_messages_group = pygame.sprite.Group() # Group for shouts

# --- Data Structure for Visualization ---
# List of tuples: (name, value, type, color)
# Type: 'radius', 'size', 'range'
constants_to_draw = [
    ("DUDE_SEPARATION_RADIUS", int(DUDE_SEPARATION_RADIUS), 'radius', BLUE), # Cast float to int
    ("DUDE_HORIZONTAL_VISION_RANGE", DUDE_HORIZONTAL_VISION_RANGE, 'range', YELLOW),
    ("EXPLOSION_RADIUS", EXPLOSION_RADIUS, 'radius', ORANGE),
    ("DUDE_HEARING_RADIUS", DUDE_HEARING_RADIUS, 'radius', PURPLE), # Changed TUPLE to PURPLE
    ("COMET_SIZE", COMET_SIZE, 'size', CYAN), # Changed color
]

# --- Spawn Function ---
def spawn_dudes():
    """ Spawns dudes up to DUDE_COUNT """
    fixed_y_position = SCREEN_HEIGHT - DUDE_SIZE # Adjust as needed
    needed = DUDE_COUNT - len(dudes_group) # Calculate how many are needed
    # print(f"Spawning {needed} dudes...") # Debug output
    for _ in range(needed): # Loop to create the required number
        x = random.randrange(50, SCREEN_WIDTH - 50)
        y = fixed_y_position
        dude = DudeObject(x, y)
        all_sprites.add(dude)
        dudes_group.add(dude)

# --- Hauptfunktion / Spielschleife ---
def main():
    # --- Pygame Initialization ---
    pygame.init() # Initialize Pygame modules
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Schwarmintelligenz Simulation - With Visualization")
    clock = pygame.time.Clock()

    # --- Font Initialization ---
    try:
        font = pygame.font.Font(None, 24) # Default font, size 24
    except pygame.error as e:
        print(f"Error loading default font: {e}")
        font = pygame.font.SysFont("arial", 20) # Fallback

    # --- Initial Spawn ---
    spawn_dudes()

    running = True
    comet_timer = 0

    # --- Visualization Layout Variables ---
    vis_start_y = 20  # Start drawing visuals near the top
    vis_spacing = 55  # Vertical space between visualized items
    vis_text_x = 20   # X position for text labels
    vis_shape_x = 250 # X position for drawing shapes (circles, lines, squares)

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # --- Add Keyboard Toggle for Visualization (Optional) ---
            # Example: Toggle with 'v' key
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_v:
            #         show_visualization = not show_visualization # Need to define show_visualization = True before the loop

        # --- Kometen Spawnen ---
        comet_timer += 1
        if comet_timer >= COMET_SPAWN_RATE:
            comet_timer = 0
            if random.random() > 0.3: # Adjust spawn probability if needed
                comet = CometObject()
                all_sprites.add(comet)
                comets_group.add(comet)

        # --- Updates ---
        # Update Dudes and collect shout requests
        shout_requests = []
        for dude in dudes_group:
            shout_direction = dude.update(dudes_group, comets_group, shout_messages_group)
            if shout_direction is not None:
                shout_pos = dude.rect.midtop
                shout_requests.append((shout_pos, shout_direction))

        # Create Shout Messages
        for pos, direction in shout_requests:
            shout = ShoutMessage(pos, direction)
            all_sprites.add(shout)
            shout_messages_group.add(shout)

        # Respawn Dudes if needed
        if len(dudes_group) < DUDE_COUNT:
            spawn_dudes()

        # Kometen updaten und Einschläge sammeln
        impact_points = []
        for comet in comets_group:
            impact = comet.update()
            if impact:
                impact_points.append(impact)

        # Explosionen erstellen
        for point in impact_points:
            explosion = ExplosionObject(point)
            all_sprites.add(explosion)
            explosions_group.add(explosion)

        # Update other groups
        explosions_group.update()
        shout_messages_group.update()

        # --- Collision Checks ---
        pygame.sprite.groupcollide(dudes_group, explosions_group, True, False, pygame.sprite.collide_mask)

        # --- Zeichnen ---
        screen.fill(BLACK)
        all_sprites.draw(screen) # Draw simulation elements first

        # --- DRAW CONSTANT VISUALIZATION ---
        current_y = vis_start_y
        for name, value, type, color in constants_to_draw:
            # Draw Text Label
            text_surface = font.render(f"{name}: {value}", True, WHITE)
            text_rect = text_surface.get_rect(topleft=(vis_text_x, current_y))
            screen.blit(text_surface, text_rect)

            # Draw Visual Representation
            shape_center_y = current_y + text_rect.height // 2

            if type == 'radius':
                radius = max(1, value) # Ensure radius is visible
                # Center the circle drawing area horizontally around vis_shape_x
                circle_center_x = vis_shape_x + radius
                pygame.draw.circle(screen, color, (circle_center_x, shape_center_y), radius, 2)
                pygame.draw.circle(screen, WHITE, (circle_center_x, shape_center_y), 2) # Center dot

            elif type == 'size':
                 # Center the square horizontally around vis_shape_x
                square_rect = pygame.Rect(vis_shape_x, shape_center_y - value // 2, value, value)
                pygame.draw.rect(screen, color, square_rect, 2)

            elif type == 'range':
                # Center the line horizontally around vis_shape_x
                line_start_x = vis_shape_x
                line_end_x = vis_shape_x + value
                pygame.draw.line(screen, color, (line_start_x, shape_center_y), (line_end_x, shape_center_y), 3)
                pygame.draw.circle(screen, WHITE, (line_start_x, shape_center_y), 3)
                pygame.draw.circle(screen, WHITE, (line_end_x, shape_center_y), 3)

            # Update Y position for next item
            shape_height = 0
            if type == 'radius': shape_height = value * 2
            elif type == 'size': shape_height = value
            elif type == 'range': shape_height = 5 # Minimal height
            current_y += max(text_rect.height, shape_height) + vis_spacing // 2 # Adjust spacing


        # --- END CONSTANT VISUALIZATION ---


        # --- Anzeige aktualisieren ---
        pygame.display.flip()

        # --- Framerate begrenzen ---
        clock.tick(FPS)

    pygame.quit()
    sys.exit() # Use sys.exit for a clean exit

# --- Programmstart ---
if __name__ == "__main__":
    main()