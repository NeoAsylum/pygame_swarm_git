# In your main game file (e.g., dudes.py)

import pygame
import random

# Import your classes
from CometClass import CometObject
from DudeClass import DudeObject          
from ExplosionClass import ExplosionObject 
from ShoutMessage import ShoutMessage   

# Import necessary constants from config
from config import (BLACK, COMET_SPAWN_RATE, DUDE_COUNT, FPS, SCREEN_HEIGHT,
                    SCREEN_WIDTH, DUDE_SIZE, # Add any other constants needed
                    SHOUT_ARROW_COLOR, SHOUT_ARROW_SIZE) # Constants needed by ShoutMessage

# --- Sprite Groups ---
# Defined globally so spawn_dudes can access them
all_sprites = pygame.sprite.Group()
dudes_group = pygame.sprite.Group()
comets_group = pygame.sprite.Group()
explosions_group = pygame.sprite.Group()
shout_messages_group = pygame.sprite.Group() # Group for shouts

# --- Spawn Function ---
def spawn_dudes():
    """ Spawns dudes up to DUDE_COUNT """
    fixed_y_position = SCREEN_HEIGHT - DUDE_SIZE # Adjust as needed
    needed = DUDE_COUNT - len(dudes_group) # Calculate how many are needed
    print(f"Spawning {needed} dudes...") # Debug output
    # --- 3. Fixed loop ---
    for _ in range(needed): # Loop to create the required number
        x = random.randrange(50, SCREEN_WIDTH - 50)
        y = fixed_y_position
        dude = DudeObject(x, y)
        all_sprites.add(dude)
        dudes_group.add(dude)

# --- Hauptfunktion / Spielschleife ---
def main():

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Schwarmintelligenz Simulation - Shouting")
    clock = pygame.time.Clock()

    # --- Initial Spawn ---
    spawn_dudes() # Call the corrected spawn function once

    running = True
    comet_timer = 0

    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Kometen Spawnen ---
        comet_timer += 1
        if comet_timer >= COMET_SPAWN_RATE:
            comet_timer = 0
            if random.random() > 0.3:
                comet = CometObject()
                all_sprites.add(comet)
                comets_group.add(comet)

        # --- Updates ---
        # Update Dudes and collect shout requests
        shout_requests = []
        for dude in dudes_group:
            # Pass all necessary groups to the dude's update method
            shout_direction = dude.update(dudes_group, comets_group, shout_messages_group)
            if shout_direction is not None:
                shout_pos = dude.rect.midtop # Position above the dude
                shout_requests.append((shout_pos, shout_direction))

        # --- 2. Create Shout Messages ---
        for pos, direction in shout_requests:
            shout = ShoutMessage(pos, direction)
            all_sprites.add(shout)
            shout_messages_group.add(shout)
        # --- End Shout Message Creation ---

        # Respawn Dudes if needed
        if len(dudes_group) < DUDE_COUNT:
            spawn_dudes() # Call the corrected spawn function

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
        shout_messages_group.update() # Update shouts (for timer/kill)

        # --- Collision Checks ---
        # Dudes <-> Explosionen
        pygame.sprite.groupcollide(dudes_group, explosions_group, True, False, pygame.sprite.collide_mask)

        # --- Zeichnen ---
        screen.fill(BLACK)
        all_sprites.draw(screen) # Draws Dudes, Comets, Explosions, and Shouts

        # --- Anzeige aktualisieren ---
        pygame.display.flip()

        # --- Framerate begrenzen ---
        clock.tick(FPS)

    pygame.quit()

# --- Programmstart ---
if __name__ == "__main__":
    main()
