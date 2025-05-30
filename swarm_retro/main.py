import pygame
import random
import csv 

from Bird_class import Bird
from Obstacles import Obstacle
from FoodClass import Food

from env import * 

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flocking Birds")
        try:
            self.font = pygame.font.Font(None, UI_FONT_SIZE)
        except NameError:
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
        self.stats_update_timer = 0
        self.frame_counter_for_logging_stats = 0
        self.frames_to_count_stats = 100

        self.num_current_birds = 0
        self.avg_cohesion = 0.0
        self.avg_alignment = 0.0
        self.avg_separation = 0.0
        self.avg_avoidance = 0.0
        self.avg_food_attraction = 0.0

        # Assuming Bird class has this class attribute
        if not hasattr(Bird, "collision_count"):
            Bird.collision_count = 0

        # CSV Logger setup
        self.csv_filename = "game_stats.csv"
        try:
            self.csv_file = open(self.csv_filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            # Write header
            self.csv_writer.writerow(["BirdCount", "AvgCohesion", "AvgAlignment", "AvgSeparation", "AvgAvoidance", "AvgFoodAttraction"])
        except IOError:
            print(f"Error: Could not open or write to {self.csv_filename}")
            self.csv_file = None 
            
    def _create_initial_birds(self):
        for _ in range(INITIAL_NUM_BIRDS):
            bird_x = random.randint(20, SCREEN_WIDTH - 20)
            bird_y = random.randint(20, SCREEN_HEIGHT - 20)
            bird = Bird(bird_x, bird_y)
            self.birds_group.add(bird)

    def _spawn_food(self):
        self.food_spawn_timer += 1
        if self.food_spawn_timer >= FOOD_SPAWN_INTERVAL_FRAMES:
            self.food_spawn_timer = 0
            if (len(self.food_group) < MAX_FOOD_ON_SCREEN or self.num_current_birds < OBSTACLE_HIGH_BIRD_THRESHOLD):
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

        self.frame_counter_for_logging_stats += STATS_UPDATE_INTERVAL_FRAMES
        if self.csv_file and self.csv_writer and self.frame_counter_for_logging_stats >= self.frames_to_count_stats:
            self.frame_counter_for_logging_stats = 0
            self.csv_writer.writerow([round(self.num_current_birds,4), round(self.avg_cohesion,4), round(self.avg_alignment,4), 
                                      round(self.avg_separation,4), round(self.avg_avoidance,4), round(self.avg_food_attraction,4)])

    def _render_text(self, text_str, position, color=None):
        default_color = BLACK if "BLACK" in globals() else (0, 0, 0)
        text_surface = self.font.render(
            text_str, True, color if color else default_color
        )
        self.screen.blit(text_surface, position)

    def _draw_ui(self):
        current_fps_val = int(self.clock.get_fps())
        stats_y_start = (
            UI_PADDING + UI_LINE_HEIGHT * 2
        )

        self._render_text(f"FPS: {current_fps_val}", (UI_PADDING, UI_PADDING))
        self._render_text(
            f"Collision-score: {Bird.collision_count}", (UI_PADDING, UI_PADDING + UI_LINE_HEIGHT)
        )
        self._render_text(
            f"Bird Count: {self.num_current_birds}", (UI_PADDING, stats_y_start)
        )

        stats_y_start += UI_LINE_HEIGHT
        self._render_text(
            f"Avg Cohesion: {self.avg_cohesion:.3f}", (UI_PADDING, stats_y_start)
        )
        self._render_text(
            f"Avg Alignment: {self.avg_alignment:.3f}",
            (UI_PADDING, stats_y_start + UI_LINE_HEIGHT),
        )
        self._render_text(
            f"Avg Separation: {self.avg_separation:.3f}",
            (UI_PADDING, stats_y_start + 2 * UI_LINE_HEIGHT),
        )
        self._render_text(
            f"Avg Avoidance: {self.avg_avoidance:.3f}",
            (UI_PADDING, stats_y_start + 3 * UI_LINE_HEIGHT),
        )
        self._render_text(
            f"Avg Food Attraction: {self.avg_food_attraction:.3f}",
            (UI_PADDING, stats_y_start + 4 * UI_LINE_HEIGHT),
        )

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update_state(self):
        self.birds_group.update(self.birds_group, self.obstacle_group, self.food_group)
        self.obstacle_group.update()

        self._spawn_food()  # Spawn food based on its timer

        self.stats_update_timer += 1

        if self.stats_update_timer >= STATS_UPDATE_INTERVAL_FRAMES:
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
            try:
                self.process_events()
                self.update_state()
                self.render()
                try:
                    target_fps = FPS
                except NameError:  # Fallback
                    target_fps = 120
                self.clock.tick(target_fps)
            except Exception as e:
                print(f"An error occurred during the game loop: {e}")
                self.running = False # Stop the game on unhandled error
        # Cleanup
        if hasattr(self, 'csv_file') and self.csv_file:
            self.csv_file.close()

# Main execution block
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
