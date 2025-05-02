# In your main game file (e.g., dudes.py)

import pygame
import random

from CometClass import CometObject
from DudeClass import DudeObject
from ExplosionClass import ExplosionObject

# Import necessary constants
from config import (BLACK, COMET_SPAWN_RATE, DUDE_COUNT, FPS, SCREEN_HEIGHT,
                    SCREEN_WIDTH, DUDE_SIZE)

# --- Hauptfunktion / Spielschleife ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Schwarmintelligenz Simulation")
    clock = pygame.time.Clock()

    # Sprite-Gruppen erstellen
    all_sprites = pygame.sprite.Group()
    dudes_group = pygame.sprite.Group()
    comets_group = pygame.sprite.Group()
    explosions_group = pygame.sprite.Group() # <-- Neue Gruppe für Explosionen

    # Dudes erstellen
    fixed_y_position = SCREEN_HEIGHT - DUDE_SIZE # Adjust as needed
    for _ in range(DUDE_COUNT):
        x = random.randrange(50, SCREEN_WIDTH - 50)
        y = fixed_y_position
        dude = DudeObject(x, y)
        all_sprites.add(dude)
        dudes_group.add(dude)

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
        # Reihenfolge wichtig: Dudes reagieren auf Kometen/andere Dudes
        dudes_group.update(dudes_group, comets_group)

        # Kometen updaten und Einschläge sammeln
        impact_points = []
        for comet in comets_group:
            impact = comet.update()
            if impact:
                impact_points.append(impact)

        # --- NEU: Explosionen erstellen ---
        for point in impact_points:
            explosion = ExplosionObject(point) # Erstelle Explosion am Einschlagpunkt
            all_sprites.add(explosion)
            explosions_group.add(explosion)

        # --- NEU: Explosionen updaten (Timer, Animation, self.kill()) ---
        explosions_group.update()

        # --- NEU: Kollision Dudes <-> Explosionen ---
        # Dudes (True) werden entfernt, Explosionen (False) bleiben (bis ihr Timer abläuft)
        pygame.sprite.groupcollide(dudes_group, explosions_group, True, False, pygame.sprite.collide_mask)

        # --- Kollision Dudes <-> Kometen (in der Luft) ---
        pygame.sprite.groupcollide(dudes_group, comets_group, True, True, pygame.sprite.collide_mask)

        # --- Zeichnen ---
        screen.fill(BLACK)
        all_sprites.draw(screen) # Zeichnet Dudes, Kometen und Explosionen

        # --- Anzeige aktualisieren ---
        pygame.display.flip()

        # --- Framerate begrenzen ---
        clock.tick(FPS)

    pygame.quit()

# --- Programmstart ---
if __name__ == "__main__":
    main()