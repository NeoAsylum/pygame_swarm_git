# pygame_swarm_git/swarm_retro/SliderManagerClass.py
import pygame
import config_retro as cfg

class SliderManager:
    def __init__(self, screen, height):
        self.screen = screen
        self.font = pygame.font.Font(None, 28)
        self.slider_width = 200
        self.slider_height = 10
        self.slider_padding = 35
        self.slider_y_offset = 60 # Abstand vom unteren Bildschirmrand nach oben
        self.slider_handle_width = 8
        self.slider_handle_height = self.slider_height + 10 # Griff ist etwas höher als die Leiste
        self.dragging_slider = None # Name des aktuell gezogenen Sliders

        # Startwerte aus der Konfiguration laden
        self.cohesion_strength = cfg.DEFAULT_COHESION
        self.alignment_strength = cfg.DEFAULT_ALIGNMENT
        self.separation_strength = cfg.DEFAULT_SEPARATION
        self.global_speed_factor = cfg.DEFAULT_SPEED
        self.avoidance_strength = cfg.DEFAULT_AVOIDANCE_SLIDER # Bezieht sich auf den Slider-Wert

        # Y-Position der untersten UI-Elemente (Slider)
        base_y = height - self.slider_y_offset # Beginnt von unten
        
        # Definition der Rechtecke für jeden Slider
        # Die Reihenfolge bestimmt die Anordnung von unten nach oben
        self.avoidance_slider_rect = pygame.Rect(
            self.slider_padding, base_y - 1 * (self.slider_height + self.slider_padding), # Unterster Slider
            self.slider_width, self.slider_height )
        self.speed_slider_rect = pygame.Rect(
            self.slider_padding, base_y - 2 * (self.slider_height + self.slider_padding),
            self.slider_width, self.slider_height )
        self.separation_slider_rect = pygame.Rect(
            self.slider_padding, base_y - 3 * (self.slider_height + self.slider_padding),
            self.slider_width, self.slider_height )
        self.alignment_slider_rect = pygame.Rect(
            self.slider_padding, base_y - 4 * (self.slider_height + self.slider_padding),
            self.slider_width, self.slider_height )
        self.cohesion_slider_rect = pygame.Rect(
            self.slider_padding, base_y - 5 * (self.slider_height + self.slider_padding), # Oberster Slider
            self.slider_width, self.slider_height )

        # Button-Definition
        self.button_width = 100 
        self.button_height = 35
        # X-Position des Buttons (rechts neben den Slider-Labels)
        button_x_start = self.slider_padding + self.slider_width + 15 + 170 # 15 für Label-Padding, 170 für Label-Breite
        # Y-Position des Buttons (auf Höhe des obersten Sliders)
        apply_button_y = self.cohesion_slider_rect.top 
        self.apply_button_rect = pygame.Rect(button_x_start, apply_button_y, self.button_width, self.button_height)
        
        self.mouse_over_apply = False # Für Hover-Effekt des Buttons

    def _draw_slider(self, rect, value, label):
        # Hintergrund der Sliderleiste
        pygame.draw.rect(self.screen, cfg.UI_SLIDER_BG_COLOR, rect, border_radius=5)
        # Gefüllter Teil der Sliderleiste
        filled_width = int(value * rect.width)
        filled_rect = pygame.Rect(rect.left, rect.top, filled_width, rect.height)
        pygame.draw.rect(self.screen, cfg.UI_SLIDER_BAR_COLOR, filled_rect, border_radius=5)
        # Slider-Griff
        handle_center_x = rect.left + max(0, min(filled_width, rect.width)) # Stelle sicher, dass Griff innerhalb der Leiste bleibt
        handle_x_pos = handle_center_x - (self.slider_handle_width // 2)
        handle_rect = pygame.Rect(handle_x_pos, rect.centery - self.slider_handle_height // 2, 
                                  self.slider_handle_width, self.slider_handle_height)
        pygame.draw.rect(self.screen, cfg.UI_SLIDER_HANDLE_COLOR, handle_rect, border_radius=3)
        # Text-Label für den Slider
        text_surface = self.font.render(f"{label}: {value:.2f}", True, cfg.UI_TEXT_COLOR)
        text_rect = text_surface.get_rect(midleft=(rect.right + 15, rect.centery)) # Rechts neben dem Slider
        self.screen.blit(text_surface, text_rect)

    def _draw_button(self, rect, text, is_hovered):
        button_color = cfg.UI_BUTTON_HOVER_COLOR if is_hovered else cfg.UI_BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, cfg.UI_TEXT_COLOR, rect, width=2, border_radius=8) # Rand
        text_surface = self.font.render(text, True, cfg.UI_BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_sliders_and_buttons(self):
        self._draw_slider(self.cohesion_slider_rect, self.cohesion_strength, "Cohesion")
        self._draw_slider(self.alignment_slider_rect, self.alignment_strength, "Alignment")
        self._draw_slider(self.separation_slider_rect, self.separation_strength, "Separation")
        self._draw_slider(self.speed_slider_rect, self.global_speed_factor, "Speed")
        self._draw_slider(self.avoidance_slider_rect, self.avoidance_strength, "Avoidance")
        self._draw_button(self.apply_button_rect, "Apply", self.mouse_over_apply)

    # --- NEU: Hilfsmethode ---
    def get_slider_rects_and_attributes(self):
        """ Gibt ein Dictionary der Slider-Rechtecke und ihrer zugehörigen Attribute zurück. """
        return {
            "cohesion": (self.cohesion_slider_rect, "cohesion_strength"),
            "alignment": (self.alignment_slider_rect, "alignment_strength"),
            "separation": (self.separation_slider_rect, "separation_strength"),
            "speed": (self.speed_slider_rect, "global_speed_factor"),
            "avoidance": (self.avoidance_slider_rect, "avoidance_strength"),
        }

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        action_to_return = None 
        self.mouse_over_apply = self.apply_button_rect.collidepoint(mouse_pos) # Hover-Effekt prüfen

        slider_rects_attrs = self.get_slider_rects_and_attributes()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Linke Maustaste
                slider_clicked_this_event = False
                for name, (rect, attr_name) in slider_rects_attrs.items():
                    if rect.collidepoint(mouse_pos):
                        self.dragging_slider = name # Merken, welcher Slider gezogen wird
                        # Wert des Sliders direkt beim Klick aktualisieren
                        setattr(self, attr_name, self._get_slider_value(mouse_pos[0], rect))
                        slider_clicked_this_event = True
                        break # Nur einen Slider pro Klick bearbeiten
                
                if not slider_clicked_this_event and self.mouse_over_apply: # Wenn auf Apply-Button geklickt
                    action_to_return = "apply"

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Linke Maustaste losgelassen
                self.dragging_slider = None # Keinen Slider mehr ziehen

        elif event.type == pygame.MOUSEMOTION and self.dragging_slider: # Maus bewegt sich, während ein Slider gezogen wird
            mouse_x = mouse_pos[0]
            # Zugehörigen Slider-Namen und Attribut finden (redundant zur Schleife oben, aber sicher)
            # slider_map = { ... } # wie in der Originalversion
            if self.dragging_slider in slider_rects_attrs:
                rect, attribute_name = slider_rects_attrs[self.dragging_slider] # Korrigierter Zugriff
                setattr(self, attribute_name, self._get_slider_value(mouse_x, rect))
        
        return action_to_return

    def _get_slider_value(self, mouse_x, slider_rect):
        """ Berechnet den Wert (0.0 bis 1.0) basierend auf der Mausposition auf dem Slider. """
        value = (mouse_x - slider_rect.left) / slider_rect.width
        return max(0.0, min(1.0, value)) # Wert auf [0, 1] beschränken

    def apply_values_to_birds(self, birds_group_or_list): # Diese Methode wird aktuell in main.py direkt gehandhabt
        """ Wendet die aktuellen Slider-Werte auf alle Vögel an. (Kann auch in main.py bleiben) """
        for bird in birds_group_or_list:
            bird.cohesion_strength = self.cohesion_strength
            bird.alignment_strength = self.alignment_strength
            bird.separation_strength = self.separation_strength
            bird.global_speed_factor = self.global_speed_factor
            bird.slider_avoidance_strength = self.avoidance_strength