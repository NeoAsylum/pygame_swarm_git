import pygame
import random

# Assuming these classes are correctly defined in their respective files
from Bird_class import Bird
from Obstacles import Obstacle
from FoodClass import Food

# Assuming env.py contains your game environment constants
# For example:
# SCREEN_WIDTH = 1800
# SCREEN_HEIGHT = 1000
# INITIAL_NUM_BIRDS = 50
# FOOD_SPAWN_INTERVAL_FRAMES = 2
# MAX_FOOD_ON_SCREEN = 30
# FOOD_SIZE = 10 # Example for food dimensions
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# UI_FONT_SIZE = 30
# UI_LINE_HEIGHT = 30
# UI_PADDING = 10
# STATS_UPDATE_INTERVAL_FRAMES = 30 # Renamed obstacle_frame_counter's threshold
# FPS = 120
# DESIRED_NUM_OBSTACLES = 8
# OBSTACLE_WIDTH = 30
# OBSTACLE_HEIGHT = 30
# OBSTACLE_SPEED = 4
# OBSTACLE_HIGH_BIRD_THRESHOLD = 120 # For the condition in manage_obstacles

from env import *  # Import constants from your env.py file


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flocking Birds")
        try:
            self.font = pygame.font.Font(None, UI_FONT_SIZE)
        except NameError:  # Fallback if UI_FONT_SIZE is not in env.py
            self.font = pygame.font.Font(None, 30)

        self.clock = pygame.time.Clock()
        self.running = True

        # Sprite groups
        self.birds_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()

        self._create_initial_birds()

        # Game state variables
        self.food_spawn_timer = 0
        self.stats_update_timer = 0  # Replaces obstacle_frame_counter

        self.num_current_birds = 0
        self.avg_cohesion = 0.0
        self.avg_alignment = 0.0
        self.avg_separation = 0.0
        self.avg_avoidance = 0.0
        self.avg_food_attraction = 0.0

        # Assuming Bird class has this class attribute
        if not hasattr(Bird, "collision_count"):
            Bird.collision_count = 0

    def _create_initial_birds(self):
        for _ in range(INITIAL_NUM_BIRDS):
            bird_x = random.randint(20, SCREEN_WIDTH - 20)
            bird_y = random.randint(20, SCREEN_HEIGHT - 20)
            # Pass screen dimensions if Bird class uses them for boundary checks
            bird = Bird(bird_x, bird_y, SCREEN_WIDTH, SCREEN_HEIGHT)
            self.birds_group.add(bird)

    def _spawn_food(self):
        self.food_spawn_timer += 1
        if self.food_spawn_timer >= FOOD_SPAWN_INTERVAL_FRAMES:
            self.food_spawn_timer = 0
            if len(self.food_group) < MAX_FOOD_ON_SCREEN:
                food_x = random.randint(10, SCREEN_WIDTH - 10 - FOOD_SIZE)
                food_y = random.randint(10, SCREEN_HEIGHT - 10 - FOOD_SIZE)
                # Assuming Food class takes x, y and optionally size
                # Adjust Food() call based on your FoodClass definition
                new_food = Food(
                    food_x, food_y
                )  # Or Food(food_x, food_y) if size is fixed in class
                self.food_group.add(new_food)

    def _manage_obstacles(self):
        """
        Ensures there are DESIRED_NUM_OBSTACLES on screen.
        Spawns one new obstacle if conditions are met.
        """
        # This condition for spawning more obstacles if num_current_birds > 120
        # was in your original code when manage_obstacles was called.
        spawn_condition_met = (
            len(self.obstacle_group) < DESIRED_NUM_OBSTACLES
            or self.num_current_birds > OBSTACLE_HIGH_BIRD_THRESHOLD
        )

        if spawn_condition_met:
            new_obstacle = Obstacle()
            self.obstacle_group.add(new_obstacle)

    def _calculate_and_update_stats(self):
        current_bird_sprites = self.birds_group.sprites()
        self.num_current_birds = len(current_bird_sprites)

        if self.num_current_birds > 0:
            # Ensure bird_sprite instances have these attributes
            self.avg_cohesion = (
                sum(getattr(b, "cohesion_strength", 0) for b in current_bird_sprites)
                / self.num_current_birds
            )
            self.avg_alignment = (
                sum(getattr(b, "alignment_strength", 0) for b in current_bird_sprites)
                / self.num_current_birds
            )
            self.avg_separation = (
                sum(getattr(b, "separation_strength", 0) for b in current_bird_sprites)
                / self.num_current_birds
            )
            self.avg_avoidance = (
                sum(getattr(b, "avoidance_strength", 0) for b in current_bird_sprites)
                / self.num_current_birds
            )
            self.avg_food_attraction = (
                sum(
                    getattr(b, "food_attraction_strength", 0)
                    for b in current_bird_sprites
                )
                / self.num_current_birds
            )
        else:
            self.avg_cohesion = 0.0
            self.avg_alignment = 0.0
            self.avg_separation = 0.0
            self.avg_avoidance = 0.0
            self.avg_food_attraction = 0.0

    def _render_text(self, text_str, position, color=None):
        default_color = BLACK if "BLACK" in globals() else (0, 0, 0)
        text_surface = self.font.render(
            text_str, True, color if color else default_color
        )
        self.screen.blit(text_surface, position)

    def _draw_ui(self):
        try:
            current_fps_val = int(self.clock.get_fps())
            padding = UI_PADDING
            line_h = UI_LINE_HEIGHT
            stats_y_start = (
                padding + line_h * 2
            )  # Adjusted start for stats below FPS and Collisions
        except NameError:  # Fallback if UI constants are not in env.py
            current_fps_val = int(self.clock.get_fps())
            padding = 10
            line_h = 30
            stats_y_start = 80

        self._render_text(f"FPS: {current_fps_val}", (padding, padding))
        self._render_text(
            f"Collision-score: {Bird.collision_count}", (padding, padding + line_h)
        )
        self._render_text(
            f"Bird Count: {self.num_current_birds}", (padding, stats_y_start)
        )

        stats_y_start += line_h  # Increment y for next stat
        self._render_text(
            f"Avg Cohesion: {self.avg_cohesion:.3f}", (padding, stats_y_start)
        )
        self._render_text(
            f"Avg Alignment: {self.avg_alignment:.3f}",
            (padding, stats_y_start + line_h),
        )
        self._render_text(
            f"Avg Separation: {self.avg_separation:.3f}",
            (padding, stats_y_start + 2 * line_h),
        )
        self._render_text(
            f"Avg Avoidance: {self.avg_avoidance:.3f}",
            (padding, stats_y_start + 3 * line_h),
        )
        self._render_text(
            f"Avg Food Attraction: {self.avg_food_attraction:.3f}",
            (padding, stats_y_start + 4 * line_h),
        )

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Add other event handling (e.g., key presses) here if needed

    def update_state(self):
        self.birds_group.update(self.birds_group, self.obstacle_group, self.food_group)
        self.obstacle_group.update()

        self._spawn_food()  # Spawn food based on its timer

        self.stats_update_timer += 1
        try:
            stats_interval = STATS_UPDATE_INTERVAL_FRAMES
        except NameError:  # Fallback if not in env.py
            stats_interval = 30

        if self.stats_update_timer >= stats_interval:
            self.stats_update_timer = 0
            self._calculate_and_update_stats()
            self._manage_obstacles()  # Manage obstacles with the same frequency as stats update, as per original code

    def render(self):
        try:
            fill_color = WHITE
        except NameError:  # Fallback
            fill_color = (255, 255, 255)
        self.screen.fill(fill_color)

        self.birds_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        self.food_group.draw(self.screen)

        self._draw_ui()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.process_events()
            self.update_state()
            self.render()
            try:
                target_fps = FPS
            except NameError:  # Fallback
                target_fps = 120
            self.clock.tick(target_fps)


# Main execution block
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
