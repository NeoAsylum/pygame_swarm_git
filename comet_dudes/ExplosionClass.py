import pygame

from config import EXPLOSION_RADIUS, EXPLOSION_DURATION, RED, ORANGE, YELLOW # Add ORANGE, YELLOW if not present

class ExplosionObject(pygame.sprite.Sprite):
    """
    Represents a temporary explosion effect that kills Dudes on contact.
    """
    def __init__(self, center_pos):
        """
        Initializes the explosion at a given center position.

        Args:
            center_pos (tuple or pygame.math.Vector2): The (x, y) coordinates for the explosion center.
        """
        super().__init__()

        self.radius = EXPLOSION_RADIUS
        self.duration = EXPLOSION_DURATION # Frames the explosion lasts
        self.max_duration = EXPLOSION_DURATION # Store initial duration for animation

        # Create the initial image (a simple circle)
        # Use SRALPHA for potential alpha transparency later
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        # Draw the initial circle (e.g., red)
        pygame.draw.circle(self.image, RED, (self.radius, self.radius), self.radius)

        self.rect = self.image.get_rect(center=center_pos)
        self.pos = pygame.math.Vector2(center_pos) # Store position if needed

        # Create a mask for pixel-perfect collision
        # Important: Create mask *after* drawing the final shape on self.image
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """
        Updates the explosion's lifetime and visual state.
        Kills itself when the duration runs out.
        """
        self.duration -= 1

        # --- Optional: Add visual effects ---
        # Example: Fade out or change color over time
        progress = self.duration / self.max_duration # 1.0 -> 0.0
        if progress < 0: progress = 0

        # Simple color change: Red -> Orange -> Yellow -> Fade
        current_radius = int(self.radius * (1.0 + (1.0-progress)*0.2)) # Slightly expand
        new_size = current_radius * 2
        # Recreate surface if size changes significantly (or use transform.scale)
        self.image = pygame.Surface([new_size, new_size], pygame.SRCALPHA)

        if progress > 0.66:
            color = RED
        elif progress > 0.33:
            color = ORANGE
        else:
            color = YELLOW

        # Set alpha based on progress (fade out)
        alpha = int(255 * progress)
        color_with_alpha = (*color, alpha) # Add alpha to the color tuple

        pygame.draw.circle(self.image, color_with_alpha, (current_radius, current_radius), current_radius)

        # Update rect and mask if image changes
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = pygame.mask.from_surface(self.image)
        # --- End Optional Visual Effects ---


        if self.duration <= 0:
            self.kill() 
