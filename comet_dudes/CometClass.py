# CometClass.py

import pygame
import random
import os

# Import constants from config
# Make sure SCREEN_HEIGHT is imported if it wasn't already
from config import COMET_SIZE, COMET_SPEED, SCREEN_HEIGHT, SCREEN_WIDTH

# --- (Pixel Data, Color Map, Transparent Color, create_surface_from_data remain the same) ---
# --- Pixel Daten für den Kometen (16x16) ---
METEOR_PIXEL_DATA = [
    "................",
    "................",
    "................",
    ".......gG.......",
    "......gGGg......",
    ".....lGGGg......",
    "....gGGGGGl.....",
    "...gGGGGGGg....",
    "..gGGGGGGGgl..",
    ".gGgGGGGGGgl..",
    ".gGGGGGGGGgR..",
    "..gGGGGGGgOR..",
    "...gGGGGgYOR..",
    "....gGGg.YO...",
    ".....lg..Y....",
    "................",
]
COLOR_MAP = {
    '.': None, 'G': (80, 80, 80), 'g': (120, 120, 120), 'l': (160, 160, 160),
    'R': (200, 0, 0), 'O': (255, 140, 0), 'Y': (255, 255, 0)
}
TRANSPARENT_COLOR = (1, 1, 1)

def create_surface_from_data(pixel_data, color_map, transparent_color):
    """ Erstellt eine Pygame Surface aus Pixel-Daten (generische Funktion). """
    height = len(pixel_data)
    width = len(pixel_data[0]) if height > 0 else 0
    if width == 0: return pygame.Surface((0, 0))
    surface = pygame.Surface((width, height))
    surface.fill(transparent_color)
    for y, row in enumerate(pixel_data):
        for x, char in enumerate(row):
            color = color_map.get(char)
            if color: surface.set_at((x, y), color)
    surface.set_colorkey(transparent_color)
    return surface


class CometObject(pygame.sprite.Sprite):
    """ Repräsentiert einen fallenden Kometen mit Pixel-Daten und Maske. """
    _cached_original_surface = None
    _cached_scaled_surface = None
    _cached_mask = None

    def __init__(self):
        super().__init__()
        if CometObject._cached_original_surface is None:
            # print("Erstelle und konvertiere Kometen-Surface...") # Optional Debug
            raw_surface = create_surface_from_data(METEOR_PIXEL_DATA, COLOR_MAP, TRANSPARENT_COLOR)
            CometObject._cached_original_surface = raw_surface.convert()

            target_width = COMET_SIZE
            target_height = COMET_SIZE
            CometObject._cached_scaled_surface = pygame.transform.scale(
                CometObject._cached_original_surface, (target_width, target_height)
            )
            CometObject._cached_mask = pygame.mask.from_surface(CometObject._cached_scaled_surface)

        self.original_image = CometObject._cached_original_surface
        self.image = CometObject._cached_scaled_surface
        self.mask = CometObject._cached_mask

        start_x = random.randrange(0, SCREEN_WIDTH)
        # Start slightly above the screen
        self.rect = self.image.get_rect(center=(start_x, -self.image.get_height()))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.vel = pygame.math.Vector2(0, COMET_SPEED)

    def update(self, *args): # Accept arguments passed by Group.update()
        """
        Bewegt den Kometen. Wenn er den Boden erreicht, wird er entfernt
        und die Einschlagposition zurückgegeben. Ansonsten wird None zurückgegeben.
        """
        self.pos += self.vel
        self.rect.center = self.pos

        # --- NEU: Bodenerkennung und Rückgabe der Position ---
        # Check if the bottom of the comet hits or passes the ground
        if self.rect.bottom >= SCREEN_HEIGHT:
            impact_pos = self.pos.copy() # Kopiere die Position zum Zeitpunkt des Einschlags
            self.kill() # Entferne den Kometen aus allen Gruppen
            return impact_pos # Gib die Einschlagposition zurück
        else:
            return None # Kein Einschlag, gib None zurück