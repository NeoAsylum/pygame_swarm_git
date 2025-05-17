import pygame

class SliderManager:
    def __init__(self, screen, height):
        self.screen = screen
        self.font = pygame.font.Font(None, 30)
        self.slider_width = 200
        self.slider_height = 20
        self.slider_padding = 30
        self.slider_y_offset = 50
        self.slider_handle_radius = 10
        self.dragging_slider = None

        # Initial values
        self.cohesion_strength = 0.10
        self.alignment_strength = 0.14
        self.separation_strength = 0.75
        self.global_speed_factor = 0.8
        self.avoidance_strength = 0.5  # NEW - Avoidance strength slider

        # Slider rectangles
        self.cohesion_slider_rect = pygame.Rect(
            self.slider_padding,
            height
            - self.slider_y_offset
            - 5 * (self.slider_height + self.slider_padding),
            self.slider_width,
            self.slider_height,
        )
        self.alignment_slider_rect = pygame.Rect(
            self.slider_padding,
            height
            - self.slider_y_offset
            - 4 * (self.slider_height + self.slider_padding),
            self.slider_width,
            self.slider_height,
        )
        self.separation_slider_rect = pygame.Rect(
            self.slider_padding,
            height
            - self.slider_y_offset
            - 3 * (self.slider_height + self.slider_padding),
            self.slider_width,
            self.slider_height,
        )
        self.speed_slider_rect = pygame.Rect(
            self.slider_padding,
            height
            - self.slider_y_offset
            - 2 * (self.slider_height + self.slider_padding),
            self.slider_width,
            self.slider_height,
        )
        self.avoidance_slider_rect = pygame.Rect(  # NEW slider for avoidance
            self.slider_padding,
            height
            - self.slider_y_offset
            - 1 * (self.slider_height + self.slider_padding),
            self.slider_width,
            self.slider_height,
        )

        # Apply button
        self.button_width = 80
        self.button_height = 30
        self.apply_button_rect = pygame.Rect(
            self.slider_padding + self.slider_width + 20,
            height
            - self.slider_y_offset
            - self.slider_height
            - self.button_height // 2,
            self.button_width,
            self.button_height,
        )

    def draw_sliders(self):
        """Draw all sliders including the new avoidance slider."""
        self._draw_slider(self.cohesion_slider_rect, self.cohesion_strength, "Cohesion")
        self._draw_slider(
            self.alignment_slider_rect, self.alignment_strength, "Alignment"
        )
        self._draw_slider(
            self.separation_slider_rect, self.separation_strength, "Separation"
        )
        self._draw_slider(self.speed_slider_rect, self.global_speed_factor, "Speed")
        self._draw_slider(
            self.avoidance_slider_rect, self.avoidance_strength, "Avoidance"
        )  # NEW

        # Draw apply button
        pygame.draw.rect(self.screen, (0, 255, 0), self.apply_button_rect)
        apply_text = self.font.render("Apply", True, (0, 0, 0))
        text_rect = apply_text.get_rect(center=self.apply_button_rect.center)
        self.screen.blit(apply_text, text_rect)

    def _draw_slider(self, rect, value, label):
        pygame.draw.rect(self.screen, (200, 200, 200), rect)
        handle_x = rect.left + int(value * rect.width)
        pygame.draw.circle(
            self.screen,
            (100, 100, 100),
            (handle_x, rect.centery),
            self.slider_handle_radius,
        )
        text = self.font.render(f"{label}: {value:.2f}", True, (0, 0, 0))
        self.screen.blit(text, (rect.left + rect.width + 10, rect.top))

    def handle_event(self, event):
        """Handle user interactions including the new avoidance slider."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self.cohesion_slider_rect.collidepoint(mouse_x, mouse_y):
                self.dragging_slider = "cohesion"
            elif self.alignment_slider_rect.collidepoint(mouse_x, mouse_y):
                self.dragging_slider = "alignment"
            elif self.separation_slider_rect.collidepoint(mouse_x, mouse_y):
                self.dragging_slider = "separation"
            elif self.speed_slider_rect.collidepoint(mouse_x, mouse_y):
                self.dragging_slider = "speed"
            elif self.avoidance_slider_rect.collidepoint(mouse_x, mouse_y):  # NEW
                self.dragging_slider = "avoidance"
            elif self.apply_button_rect.collidepoint(mouse_x, mouse_y):
                return "apply"
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_slider = None

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
            setattr(
                self,
                f"{self.dragging_slider}_strength",
                self._get_slider_value(event.pos[0], getattr(self, f"{self.dragging_slider}_slider_rect")),
            )

    def _get_slider_value(self, mouse_x, slider_rect):
        value = (mouse_x - slider_rect.left) / slider_rect.width
        return max(0.0, min(1.0, value))

    def apply_values_to_birds(self, birds):
        """Apply all slider values to birds including avoidance strength."""
        for bird in birds:
            bird.cohesion_strength = self.cohesion_strength
            bird.alignment_strength = self.alignment_strength
            bird.separation_strength = self.separation_strength
            bird.global_speed_factor = self.global_speed_factor
            bird.avoidance_strength = self.avoidance_strength  # NEW