import os
from plot import GamePlotter
import pygame
import random
from Bird_class import Bird
from Obstacles import Obstacle
from FoodClass import Food
from env import *


class Game:
    def __init__(self):
        pygame.init()
        window_pos_x = 50
        window_pos_y = 50 
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{window_pos_x},{window_pos_y}"

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        pygame.display.set_caption("Flocking Birds")
        self.font = pygame.font.Font(None, UI_FONT_SIZE)
        self.button_font = pygame.font.Font(None, UI_FONT_SIZE - 4)

        self.clock = pygame.time.Clock()
        self.running = True

        self.birds_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()
        self._create_initial_birds()

        self.food_spawn_timer = 0
        self.stats_update_timer = 0
        self.frame_counter_for_logging_stats = 0

        self.num_current_birds = 0

        # --- Data Storage for Graph (In-Memory Lists) ---
        self.graph_time_steps = []
        self.graph_data = {
            "AvgCohesion": [],
            "AvgAlignment": [],
            "AvgSeparation": [],
            "AvgAvoidance": [],
            "AvgFoodAttraction": [],
            "AvgAvoidanceDistance": [],
        }
        self.data_point_counter = 0

        # --- Matplotlib Graph Setup via GamePlotter ---
        self.plotter = GamePlotter()

        # --- Pygame Button for Graph ---
        self.toggle_graph_button_rect = pygame.Rect(
            SCREEN_WIDTH - 140 - UI_PADDING,
            UI_PADDING,
            140,
            UI_LINE_HEIGHT + 5,
        )
        self.button_color = (100, 150, 200)  # Muted blue
        self.button_hover_color = (120, 170, 220) # Lighter muted blue
        self.button_text_color = WHITE # White text for better contrast

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
            if len(self.food_group) < MAX_FOOD_ON_SCREEN:
                self.food_group.add(
                    Food(
                        random.randint(10, SCREEN_WIDTH - 10 - FOOD_SIZE),
                        random.randint(10, SCREEN_HEIGHT - 10 - FOOD_SIZE),
                    )
                )

    def _manage_obstacles(self):
        # Spawn if below desired or if bird count is high (even if desired met)
        if self.num_current_birds > OBSTACLE_HIGH_BIRD_THRESHOLD:
            how_many_too_many = int(
                round((self.num_current_birds - OBSTACLE_HIGH_BIRD_THRESHOLD) / 10, 0)
            )
            for _ in range(how_many_too_many):
                new_obstacle = Obstacle()
                self.obstacle_group.add(new_obstacle)
        else:
            if len(self.obstacle_group) < DESIRED_NUM_OBSTACLES:
                new_obstacle = Obstacle()
                self.obstacle_group.add(new_obstacle)

    def _calculate_and_update_stats(self):
        current_bird_sprites = self.birds_group.sprites()
        self.num_current_birds = len(current_bird_sprites)

        if self.num_current_birds > 0:
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
            self.avg_obstacle_avoidance_distance = (
                sum(
                    getattr(b, "obstacle_avoidance_distance", 0)
                    for b in current_bird_sprites
                )
                / self.num_current_birds
            )
        else:
            self.avg_cohesion = self.avg_alignment = self.avg_separation = (
                self.avg_avoidance
            ) = self.avg_food_attraction = self.avg_obstacle_avoidance_distance = 0.0

        self.frame_counter_for_logging_stats += 1
        if (
            self.frame_counter_for_logging_stats
            >= STATS_UPDATE_INTERVAL_FRAMES / STATE_UPDATE_INTERVAL_FRAMES
        ):
            self.frame_counter_for_logging_stats = 0
            self.graph_time_steps.append(self.data_point_counter)
            self.graph_data["AvgCohesion"].append(self.avg_cohesion)
            self.graph_data["AvgAlignment"].append(self.avg_alignment)
            self.graph_data["AvgSeparation"].append(self.avg_separation)
            self.graph_data["AvgAvoidance"].append(self.avg_avoidance)
            self.graph_data["AvgFoodAttraction"].append(self.avg_food_attraction)
            self.graph_data["AvgAvoidanceDistance"].append(
                self.avg_obstacle_avoidance_distance
            )

            if self.plotter.is_graph_showing:
                self.plotter.update_plot_with_new_data(
                    self.graph_time_steps, self.graph_data
                )
            self.data_point_counter += 1

    def _render_text(self, text_str, position, font_obj=None):
        use_font = font_obj if font_obj else self.font
        text_surface = use_font.render(text_str, True, BLACK)
        self.screen.blit(text_surface, position)

    def _draw_ui(self):
        current_fps_val = int(self.clock.get_fps())
        pad = UI_PADDING
        line_h = UI_LINE_HEIGHT

        self._render_text(f"FPS: {current_fps_val}", (pad, pad))
        self._render_text(f"Bird Count: {self.num_current_birds}", (pad, pad + line_h))

        mouse_pos = pygame.mouse.get_pos()

        ## plot Graph Button logic
        current_button_color = (
            self.button_hover_color
            if self.toggle_graph_button_rect.collidepoint(mouse_pos)
            else self.button_color
        )
        pygame.draw.rect(
            self.screen, current_button_color, self.toggle_graph_button_rect
        )
        pygame.draw.rect(
            self.screen, self.button_text_color, self.toggle_graph_button_rect, 1
        )

        text_surf = self.button_font.render(
            (
                "Graph: ON"
                if self.plotter.is_graph_showing and self.plotter.fig
                else "Graph: OFF"
            ),
            True,
            self.button_text_color,
        )
        self.screen.blit(
            text_surf,
            text_surf.get_rect(center=self.toggle_graph_button_rect.center),
        )

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            ##Let matplotlib window appear or disappear
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.toggle_graph_button_rect.collidepoint(event.pos):
                        self.plotter.toggle_graph_window(
                            self.graph_time_steps, self.graph_data
                        )
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    self.plotter.toggle_graph_window(
                        self.graph_time_steps, self.graph_data
                    )

    def update_state(self):
        self.birds_group.update(self.birds_group, self.obstacle_group, self.food_group)
        self.obstacle_group.update()
        self._spawn_food()
        self.stats_update_timer += 1
        if self.stats_update_timer >= STATE_UPDATE_INTERVAL_FRAMES:
            self.stats_update_timer = 0
            self._calculate_and_update_stats()
            self._manage_obstacles()

    def render(self):
        self.screen.fill(SKY_BLUE) # Use new background color
        self.birds_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        self.food_group.draw(self.screen)
        self._draw_ui()
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                self.process_events()
                self.update_state()
                self.render()

                # Check if matplotlib window was closed by user via 'X' button
                if (
                    self.plotter.is_graph_showing
                    and self.plotter.fig
                    and (
                        not hasattr(self.plotter.fig.canvas.manager, "window")
                    )
                ):
                    self.plotter.close_graph_window()  # Ensure state is consistent
                self.clock.tick(FPS)
        except Exception as e:
            print(f"An critical error occurred during the game loop: {e}")
            import traceback

            traceback.print_exc()
            self.running = False
        finally:
            self.plotter.close_graph_window()
            print("Matplotlib graph resources cleaned up.")
            pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
