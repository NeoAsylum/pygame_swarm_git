import pygame
import random
import math # Import math for copysign

# Import constants from config
from config import (AVOID_FACTOR, # ALIGNMENT_FACTOR removed
                    DUDE_MAX_SPEED, DUDE_SEPARATION_RADIUS,
                    DUDE_SIZE, SCREEN_WIDTH,
                    DUDE_HORIZONTAL_VISION_RANGE, SEPARATION_FACTOR, SHOUT_COOLDOWN_FRAMES, WANDER_STRENGTH,SHOUT_REACTION_FACTOR,
                    DUDE_HEARING_RADIUS
                    )

# --- (Pixel Data, Color Map, create_surface_from_data remain the same) ---
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
    if width == 0: return pygame.Surface((0, 0))
    surface = pygame.Surface((width, height)); surface.fill(transparent_color)
    for y, row in enumerate(pixel_data):
        for x, char in enumerate(row):
            color = color_map.get(char)
            if color: surface.set_at((x, y), color)
    surface.set_colorkey(transparent_color)
    return surface

    

class DudeObject(pygame.sprite.Sprite):
    """
    Represents an agent (Dude) operating only on the X-axis.
    Reacts to shouts and avoids comets based on horizontal distance. Shouts every frame if comet seen.
    """
    _cached_original_surface = None
    _cached_scaled_surface = None
    _cached_mask = None

    def __init__(self, x, y): # y is only for initial rect placement
        super().__init__()
        if DudeObject._cached_original_surface is None:
            # print("Erstelle und konvertiere Dude-Surface...") # Debug
            raw_surface = create_surface_from_data(DUDE_PIXEL_DATA, DUDE_COLOR_MAP, DUDE_TRANSPARENT_COLOR)
            DudeObject._cached_original_surface = raw_surface.convert()
            original_width = DudeObject._cached_original_surface.get_width()
            original_height = DudeObject._cached_original_surface.get_height()
            target_height = DUDE_SIZE
            scale_factor = target_height / original_height
            target_width = int(original_width * scale_factor)
            DudeObject._cached_scaled_surface = pygame.transform.scale(
                DudeObject._cached_original_surface, (target_width, target_height)
            )
            DudeObject._cached_mask = pygame.mask.from_surface(DudeObject._cached_scaled_surface)

        self.original_image = DudeObject._cached_original_surface
        self.image = DudeObject._cached_scaled_surface
        self.mask = DudeObject._cached_mask
        # Set initial rect using x and the fixed y from argument
        self.rect = self.image.get_rect(center=(x, y))

        # --- Position and Velocity are now floats for X-axis only ---
        self.pos_x = float(x)
        self.vel_x = random.choice([-1.0, 1.0]) * DUDE_MAX_SPEED * 0.5 # Start slower
        self.shout_cooldown_timer = 0
        self.heard_messages = [] # Stores currently heard ShoutMessage objects

    def calculate_separation(self, all_dudes) -> float:
        """
        Calculates a steering force to push away from nearby Dudes.
        """
        steer_sep_x = 0.0
        neighbor_count = 0
        for other_dude in all_dudes:
            if other_dude is self:
                continue # Skip self

            # Calculate distance on X-axis only
            diff_x = self.pos_x - other_dude.pos_x
            distance = abs(diff_x)

            # Check if the other dude is within the separation radius and not at the exact same spot
            if 0 < distance < DUDE_SEPARATION_RADIUS:
                # Calculate repulsion force (stronger for closer dudes)
                # Points away from the other dude (proportional to diff_x)
                # Scales inversely with distance (dividing by distance makes it stronger when close)
                repulsion_force_x = diff_x / (distance * distance + 0.001) # Inverse square + epsilon
                # Or simpler inverse: repulsion_force_x = diff_x / (distance + 0.001)

                steer_sep_x += repulsion_force_x
                neighbor_count += 1

        if neighbor_count > 0:
            steer_sep_x *= SEPARATION_FACTOR

        return steer_sep_x

    # --- Steering Calculation Methods ---
    def calculate_avoidance(self, all_comets) -> tuple[float, int | None]:
        """
        Calculates steering force based only on horizontal distance to comets above.
        Returns: (steering_force_x, direction_to_shout [-1 left, 1 right] or None)
        """
        comets_in_range = []
        steer_force = 0.0
        shout_direction = None

        for comet in all_comets:
            # Check only horizontal distance
            horizontal_dist = self.pos_x - comet.pos.x # Use comet's vector pos.x
            # Comet is implicitly "above" since they fall
            if 0 < abs(horizontal_dist) < DUDE_HORIZONTAL_VISION_RANGE:
                direction_away = math.copysign(1, horizontal_dist) # 1 to move right, -1 to move left
                comets_in_range.append((abs(horizontal_dist), direction_away))

        if comets_in_range:
            comets_in_range.sort(key=lambda item: item[0]) # Sort by distance
            closest_dist_x, direction_to_move = comets_in_range[0]
            shout_direction = int(direction_to_move)
            # Strength based on horizontal distance
            # Desired X velocity
            desired_avoid_vel_x = direction_to_move * DUDE_MAX_SPEED
            # Calculate steering force for X velocity
            steer_force = (desired_avoid_vel_x - self.vel_x) * AVOID_FACTOR

        return steer_force, shout_direction

    def calculate_shout_reaction(self) -> float:
        """
        Calculates steering force based on the direction of the CLOSEST heard message.
        """
        steer_force = 0.0
        if not self.heard_messages:
            return 0.0 # No messages, no reaction force

        min_distance = float('inf')  # Initialize minimum distance to infinity
        closest_message_direction = 0  # Initialize direction (0 means no valid message found yet)

        # Find the message closest to the Dude's current position
        for msg in self.heard_messages:
            # Calculate horizontal distance between dude's center and message's center
            # Assumes msg is a Sprite with a 'rect' attribute
            if hasattr(msg, 'rect'): # Safety check
                distance = abs(self.pos_x - msg.rect.centerx)

                # If this message is closer than the current minimum
                if distance < min_distance:
                    min_distance = distance
                    closest_message_direction = msg.direction # Store the direction of this closest message
            else:
                # Optional: Log a warning if a message doesn't have a rect
                # print(f"Warning: Heard object {msg} doesn't have a 'rect' attribute.")
                pass


        # If a closest message was found (i.e., its direction is not 0)
        if closest_message_direction != 0:
            # The target direction is simply the direction of the closest message
            target_direction = float(closest_message_direction) # Should be -1.0 or 1.0

            # Calculate the desired velocity based on reacting to the closest shout
            desired_shout_vel_x = target_direction * DUDE_MAX_SPEED

            # Calculate the steering force needed to change current velocity towards desired velocity
            steer_force = (desired_shout_vel_x - self.vel_x) * SHOUT_REACTION_FACTOR

        # Return the calculated steering force (will be 0.0 if no messages were heard or found)
        return steer_force

    def calculate_wander(self) -> float:
         """ Calculates a small random horizontal steering force. """
         return random.uniform(-1.0, 1.0) * WANDER_STRENGTH # Ensure float

    def update(self, all_dudes, all_comets, shout_messages_group) -> int | None:
        """ Updates heard messages, calculates steering forces, updates velocity, handles movement. """
        # --- Update Heard Messages ---
        current_heard = self.heard_messages[:]
         # --- DECREMENT SHOUT COOLDOWN TIMER ---
        if self.shout_cooldown_timer > 0:
            self.shout_cooldown_timer -= 1
        self.heard_messages = []
        for msg in current_heard:
            if msg.alive(): self.heard_messages.append(msg)

        for shout in shout_messages_group:
            if shout not in self.heard_messages:
                # Check distance based only on X-coordinates
                dist_x = abs(self.pos_x - shout.rect.centerx)
                if dist_x < DUDE_HEARING_RADIUS:
                    self.heard_messages.append(shout)

        # --- Calculate Steering Forces ---
        final_shout_direction = None

        steer_avoid_x, seen_comet_direction = self.calculate_avoidance(all_comets)
        steer_shout_react_x = self.calculate_shout_reaction()
        steer_wander_x = self.calculate_wander()
        steer_sep_x = self.calculate_separation(all_dudes)

        # --- Determine if this dude should shout (No Cooldown Check) ---
        if seen_comet_direction is not None and self.shout_cooldown_timer <= 0:
            final_shout_direction = seen_comet_direction
            self.shout_cooldown_timer = SHOUT_COOLDOWN_FRAMES

        # --- Combine Steering Forces ---
        final_steer_x = steer_avoid_x + steer_shout_react_x + steer_wander_x + steer_sep_x

        # --- Apply Physics to X-Velocity ---
        self.vel_x += final_steer_x
        # Limit speed
        if abs(self.vel_x) > DUDE_MAX_SPEED:
            self.vel_x = math.copysign(DUDE_MAX_SPEED, self.vel_x)

        # --- Collision Prevention before Position Update ---
        next_pos_x = self.pos_x + self.vel_x
        next_rect = self.rect.copy()
        next_rect.centerx = round(next_pos_x)
        self.pos_x = next_pos_x

        # --- Update Rect Position ---
        self.rect.centerx = round(self.pos_x)

        # --- Screen Boundaries ---
        if self.rect.left > SCREEN_WIDTH:
             self.pos_x = -self.rect.width / 2.0
             self.rect.centerx = round(self.pos_x)
        elif self.rect.right < 0:
             self.pos_x = SCREEN_WIDTH + self.rect.width / 2.0
             self.rect.centerx = round(self.pos_x)

        return final_shout_direction
