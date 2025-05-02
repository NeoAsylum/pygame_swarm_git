import pygame

# Import constants (ensure these are in your config.py)
# SHOUT_FONT_SIZE is removed
from config import SHOUT_DURATION, SHOUT_ARROW_SIZE, SHOUT_ARROW_COLOR

class ShoutMessage(pygame.sprite.Sprite):
    """
    Represents a visible, temporary arrow message (left or right)
    shouted by a Dude.
    """
    # Font is no longer needed
    # font = None

    def __init__(self, shout_pos, direction):
        """
        Initializes the shout arrow above a position.

        Args:
            shout_pos (tuple): The (x, y) coordinates for the arrow center (e.g., dude.rect.midtop).
            direction (int): -1 for left arrow, 1 for right arrow.
        """
        super().__init__()

        # Font check removed

        self.duration = SHOUT_DURATION
        self.direction = direction # Store the direction of the warning

        # --- Draw Arrow instead of Text ---
        arrow_width, arrow_height = SHOUT_ARROW_SIZE
        # Create a transparent surface for the arrow
        self.image = pygame.Surface([arrow_width, arrow_height], pygame.SRCALPHA)

        # Define points for the arrow polygon
        if direction < 0: # Point Left
            points = [
                (0, arrow_height // 2),         # Tip pointing left
                (arrow_width, 0),               # Top right corner
                (arrow_width, arrow_height)     # Bottom right corner
            ]
        else: # Point Right
            points = [
                (arrow_width, arrow_height // 2), # Tip pointing right
                (0, 0),                         # Top left corner
                (0, arrow_height)               # Bottom left corner
            ]

        # Draw the filled arrow polygon
        pygame.draw.polygon(self.image, SHOUT_ARROW_COLOR, points)

        # --- End Arrow Drawing ---

        # Set position slightly above the shout_pos (using the new image rect)
        self.rect = self.image.get_rect(centerx=shout_pos[0], bottom=shout_pos[1] - 5) # Position above head

        # No mask needed unless dudes collide with arrows

    def update(self):
        """ Decrements duration and kills the message when time runs out. """
        self.duration -= 1
        if self.duration <= 0:
            self.kill() # Remove from all groups
