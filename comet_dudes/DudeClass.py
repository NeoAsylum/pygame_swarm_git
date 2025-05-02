# Removed: from numpy import double
import pygame
import random
import math # Import math for copysign

# Import constants from config
from config import (ALIGNMENT_FACTOR, AVOID_FACTOR, # BLUE removed if not needed
                    DUDE_MAX_SPEED, DUDE_NEIGHBOR_RADIUS, DUDE_SIZE,
                    SCREEN_HEIGHT, SCREEN_WIDTH,
                    DUDE_HORIZONTAL_VISION_RANGE, WANDER_STRENGTH)

# --- Pixel Daten & Farben für den Dude ---
DUDE_PIXEL_DATA = [
    "....WW....",
    "...WWWW...",
    "...BBBB...", # Kopf/Körper Grenze
    "...BSSB...", # Shirt
    "..BSSBSB..",
    ".B.BSSB.B.", # Arme
    "...BSSB...",
    "...BSSB...",
    "...BBBB...", # Körper/Beine Grenze
    "...B..B...",
    "..B....B..",
    ".B......B.",
    "B........B",
    "..........",
    "..........",
    "..........",
]
DUDE_COLOR_MAP = {
    '.': None, # Transparent
    'B': (0, 0, 0),       # Schwarz
    'W': (255, 255, 255), # Weiß
    'S': (0, 0, 200)      # Blau (Shirt)
}
DUDE_TRANSPARENT_COLOR = (1, 2, 3) # Eindeutige transparente Farbe

def create_surface_from_data(pixel_data, color_map, transparent_color):
    """ Erstellt eine Pygame Surface aus Pixel-Daten (generische Funktion). """
    height = len(pixel_data)
    width = len(pixel_data[0]) if height > 0 else 0
    if width == 0:
        return pygame.Surface((0, 0))

    surface = pygame.Surface((width, height))
    surface.fill(transparent_color)

    for y, row in enumerate(pixel_data):
        for x, char in enumerate(row):
            color = color_map.get(char)
            if color:
                surface.set_at((x, y), color)

    surface.set_colorkey(transparent_color)
    # .convert() wird später aufgerufen
    return surface

class DudeObject(pygame.sprite.Sprite):
    """
    Represents an agent (Dude) with pixel art texture.
    """
    # Klassenvariablen zum Cachen der konvertierten Surface
    _cached_original_surface = None
    _cached_scaled_surface = None

    def __init__(self, x, y): # y is the fixed vertical position
        super().__init__()

        # Erstelle/Konvertiere die Surface nur beim ersten Mal
        if DudeObject._cached_original_surface is None:
            print("Erstelle und konvertiere Dude-Surface...") # Debug
            raw_surface = create_surface_from_data(DUDE_PIXEL_DATA, DUDE_COLOR_MAP, DUDE_TRANSPARENT_COLOR)
            DudeObject._cached_original_surface = raw_surface.convert() # Konvertieren nach Pygame-Init

            # Skaliere und cache direkt
            # Berechne Zielgröße basierend auf DUDE_SIZE (z.B. Höhe = DUDE_SIZE * 2)
            # Behalte das Seitenverhältnis der Pixel-Art bei
            original_width = DudeObject._cached_original_surface.get_width()
            original_height = DudeObject._cached_original_surface.get_height()
            target_height = DUDE_SIZE # Zielhöhe
            scale_factor = target_height / original_height
            target_width = int(original_width * scale_factor)

            DudeObject._cached_scaled_surface = pygame.transform.scale(
                DudeObject._cached_original_surface, (target_width, target_height)
            )

        # Verwende die gecachten Surfaces
        self.original_image = DudeObject._cached_original_surface
        self.image = DudeObject._cached_scaled_surface # Direkt die skalierte Version

        # self.image = pygame.Surface([DUDE_SIZE * 2, DUDE_SIZE * 2], pygame.SRCALPHA) # Alt
        # pygame.draw.circle(self.image, BLUE, (DUDE_SIZE, DUDE_SIZE), DUDE_SIZE)     # Alt
        self.rect = self.image.get_rect(center=(x, y))

        # Position and Movement Vectors
        self.fixed_y = y # Store the fixed Y-position
        self.pos = pygame.math.Vector2(x, self.fixed_y)

        # Initial velocity is purely horizontal
        initial_vel_x = random.choice([-1, 1]) * DUDE_MAX_SPEED * 0.5 # Start slower
        self.vel = pygame.math.Vector2(initial_vel_x, 0)

    # --- Steering Calculation Methods ---
    def calculate_avoidance(self, all_comets) -> float: # Renamed, type hint float
        """ Calculates the horizontal steering force to avoid nearby comets. """
        comets_in_range = []
        steer_force = 0.0 # Default to 0
        for comet in all_comets:
            horizontal_dist = self.pos.x - comet.pos.x
            if 0 < abs(horizontal_dist) < DUDE_HORIZONTAL_VISION_RANGE:
                comets_in_range.append((horizontal_dist, comet))

        if comets_in_range:
            comets_in_range.sort(key=lambda item: abs(item[0]))
            closest_dist_x, _ = comets_in_range[0]
            if abs(closest_dist_x) < 1: closest_dist_x = math.copysign(1, closest_dist_x)

            avoid_strength = (DUDE_HORIZONTAL_VISION_RANGE / abs(closest_dist_x))
            desired_avoid_vel_x = math.copysign(DUDE_MAX_SPEED, closest_dist_x)
            steer_force = (desired_avoid_vel_x - self.vel.x) * AVOID_FACTOR * avoid_strength

        return steer_force # Return calculated force or 0.0

    def calculate_alignment(self, all_dudes) -> float: # Renamed, type hint float
        """ Calculates the horizontal steering force to align with nearby dudes. """
        nearby_dudes_vel_x_sum = 0.0
        nearby_dudes_count = 0
        steer_force = 0.0 # Default to 0
        for other_dude in all_dudes:
            if other_dude != self:
                dist = (self.pos - other_dude.pos).length()
                if 0 < dist < DUDE_NEIGHBOR_RADIUS:
                    nearby_dudes_vel_x_sum += other_dude.vel.x
                    nearby_dudes_count += 1

        if nearby_dudes_count > 0:
            avg_neighbor_vel_x = nearby_dudes_vel_x_sum / nearby_dudes_count
            desired_align_vel_x = avg_neighbor_vel_x
            steer_force = (desired_align_vel_x - self.vel.x) * ALIGNMENT_FACTOR

        return steer_force # Return calculated force or 0.0

    def calculate_wander(self) -> float:
         """ Calculates a small random horizontal steering force. """
         return random.uniform(-1, 1) * WANDER_STRENGTH

    def update(self, all_dudes, all_comets):
        """ Calculates steering forces and updates the dude's state. """

        # --- Calculate Steering Forces ---
        steer_avoid_x = self.calculate_avoidance(all_comets)
        steer_align_x = 0.0
        steer_wander_x = 0.0

        # Only align and wander if avoidance force is negligible
        if abs(steer_avoid_x) < 0.01:
             # --- FIX: Assign to steer_align_x ---
            steer_align_x = self.calculate_alignment(all_dudes)
            steer_wander_x = self.calculate_wander()

        # --- Combine Steering Forces ---
        final_steer_x = steer_avoid_x + steer_align_x + steer_wander_x

        # --- Apply Physics ---
        self.vel.x += final_steer_x
        self.vel.y = 0 # Ensure Y velocity remains exactly 0

        # Limit speed
        if abs(self.vel.x) > DUDE_MAX_SPEED:
            self.vel.x = math.copysign(DUDE_MAX_SPEED, self.vel.x)

        # --- Update Position ---
        self.pos.x += self.vel.x
        self.pos.y = self.fixed_y # Ensure Y position remains fixed

        # Update the sprite's rectangle position
        self.rect.centerx = self.pos.x
        self.rect.centery = self.pos.y # Keep Y centered on the fixed line

        # --- Screen Boundaries (Wrap Around for X-axis) ---
        if self.pos.x > SCREEN_WIDTH + self.rect.width // 2: # Adjust buffer based on actual width
             self.pos.x = -self.rect.width // 2
        elif self.pos.x < -self.rect.width // 2:
             self.pos.x = SCREEN_WIDTH + self.rect.width // 2

