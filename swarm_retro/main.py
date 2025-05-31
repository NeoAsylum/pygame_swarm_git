import matplotlib

from plot import GamePlotter
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
import pygame
import random

# Assuming these exist and are correctly imported
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
            self.button_font = pygame.font.Font(None, UI_FONT_SIZE - 4 if UI_FONT_SIZE > 20 else 16)
        except NameError: # Fallback if UI_FONT_SIZE is not defined
            self.font = pygame.font.Font(None, 30)
            self.button_font = pygame.font.Font(None, 24)

        self.clock = pygame.time.Clock()
        self.running = True

        self.birds_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()
        self._create_initial_birds()

        self.food_spawn_timer = 0
        self.stats_update_timer = 0
        self.frame_counter_for_logging_stats = 0
        self.frames_to_count_stats = 3 

        self.num_current_birds = 0
        self.avg_cohesion = 0.0
        self.avg_alignment = 0.0
        self.avg_separation = 0.0
        self.avg_avoidance = 0.0
        self.avg_food_attraction = 0.0

        if not hasattr(Bird, "collision_count"):
            Bird.collision_count = 0

        # --- Data Storage for Graph (In-Memory Lists) ---
        self.graph_time_steps = [] 
        self.graph_data = { 
            "AvgCohesion": [],
            "AvgAlignment": [],
            "AvgSeparation": [],
            "AvgAvoidance": [],
            "AvgFoodAttraction": [],
        }
        self.data_point_counter = 0 

        # --- Matplotlib Graph Setup via GamePlotter ---
        self.plotter = GamePlotter(initial_is_showing=False) # Or True to start open

        # --- Pygame Button for Graph ---
        button_width = 140
        button_height = (UI_LINE_HEIGHT) + 5
        self.toggle_graph_button_rect = pygame.Rect(
            SCREEN_WIDTH - button_width - UI_PADDING,
            UI_PADDING,
            button_width, button_height
        )
        self.button_color = (200, 200, 200)
        self.button_hover_color = (230, 230, 230)
        self.button_text_color = BLACK

    def _create_initial_birds(self):
        for _ in range(INITIAL_NUM_BIRDS):
            bird_x = random.randint(20, SCREEN_WIDTH - 20)
            bird_y = random.randint(20, SCREEN_HEIGHT - 20)
            bird = Bird(bird_x, bird_y)
            self.birds_group.add(bird)

    def _spawn_food(self):
        self.food_spawn_timer += 1
        f_spawn_interval = FOOD_SPAWN_INTERVAL_FRAMES
        if self.food_spawn_timer >= f_spawn_interval:
            self.food_spawn_timer = 0
            max_food = MAX_FOOD_ON_SCREEN
            obs_thresh = OBSTACLE_HIGH_BIRD_THRESHOLD
            f_size = FOOD_SIZE
            if (len(self.food_group) < max_food or self.num_current_birds < obs_thresh):
                food_x = random.randint(10, SCREEN_WIDTH - 10 - f_size)
                food_y = random.randint(10, SCREEN_HEIGHT - 10 - f_size)
                new_food = Food(food_x, food_y)
                self.food_group.add(new_food)

    def _manage_obstacles(self):
        desired_obs = DESIRED_NUM_OBSTACLES
        obs_thresh = OBSTACLE_HIGH_BIRD_THRESHOLD
        # Spawn if below desired or if bird count is high (even if desired met)
        spawn_condition_met = (
            len(self.obstacle_group) < desired_obs or
            (len(self.obstacle_group) < desired_obs + 2 and self.num_current_birds > obs_thresh) # Example: allow a couple more if many birds
        )
        if spawn_condition_met:
            new_obstacle = Obstacle()
            self.obstacle_group.add(new_obstacle)

    def _calculate_and_update_stats(self):
        current_bird_sprites = self.birds_group.sprites()
        self.num_current_birds = len(current_bird_sprites)

        if self.num_current_birds > 0:
            self.avg_cohesion = sum(getattr(b, "cohesion_strength", 0) for b in current_bird_sprites) / self.num_current_birds
            self.avg_alignment = sum(getattr(b, "alignment_strength", 0) for b in current_bird_sprites) / self.num_current_birds
            self.avg_separation = sum(getattr(b, "separation_strength", 0) for b in current_bird_sprites) / self.num_current_birds
            self.avg_avoidance = sum(getattr(b, "avoidance_strength", 0) for b in current_bird_sprites) / self.num_current_birds
            self.avg_food_attraction = sum(getattr(b, "food_attraction_strength", 0) for b in current_bird_sprites) / self.num_current_birds
        else:
            self.avg_cohesion = self.avg_alignment = self.avg_separation = self.avg_avoidance = self.avg_food_attraction = 0.0

        self.frame_counter_for_logging_stats += 1
        if self.frame_counter_for_logging_stats >= self.frames_to_count_stats:
            self.frame_counter_for_logging_stats = 0

            self.graph_time_steps.append(self.data_point_counter)
            self.graph_data["AvgCohesion"].append(self.avg_cohesion)
            self.graph_data["AvgAlignment"].append(self.avg_alignment)
            self.graph_data["AvgSeparation"].append(self.avg_separation)
            self.graph_data["AvgAvoidance"].append(self.avg_avoidance)
            self.graph_data["AvgFoodAttraction"].append(self.avg_food_attraction)
            
            if self.plotter.is_graph_showing:
                self.plotter.update_plot_with_new_data(self.graph_time_steps, self.graph_data)
            self.data_point_counter += 1

    def _render_text(self, text_str, position, color=None, font_obj=None):
        use_font = font_obj if font_obj else self.font
        default_color = BLACK if "BLACK" in globals() else (0, 0, 0)
        text_surface = use_font.render(text_str, True, color if color else default_color)
        self.screen.blit(text_surface, position)

    def _draw_ui(self):
        current_fps_val = int(self.clock.get_fps())
        pad = UI_PADDING if 'UI_PADDING' in globals() else 10
        line_h = UI_LINE_HEIGHT if 'UI_LINE_HEIGHT' in globals() else 20

        self._render_text(f"FPS: {current_fps_val}", (pad, pad))
        self._render_text(f"Bird Count: {self.num_current_birds}", (pad, pad + line_h))

        mouse_pos = pygame.mouse.get_pos()
        current_button_color = self.button_hover_color if self.toggle_graph_button_rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, current_button_color, self.toggle_graph_button_rect)
        pygame.draw.rect(self.screen, self.button_text_color, self.toggle_graph_button_rect, 1) 

        button_text_str = "Graph: ON" if self.plotter.is_graph_showing and self.plotter.fig else "Graph: OFF"
        text_surf = self.button_font.render(button_text_str, True, self.button_text_color)
        text_rect = text_surf.get_rect(center=self.toggle_graph_button_rect.center)
        self.screen.blit(text_surf, text_rect)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if self.toggle_graph_button_rect.collidepoint(event.pos):
                        self.plotter.toggle_graph_window(self.graph_time_steps, self.graph_data)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: 
                    self.plotter.toggle_graph_window(self.graph_time_steps, self.graph_data)

    def update_state(self):
        self.birds_group.update(self.birds_group, self.obstacle_group, self.food_group)
        self.obstacle_group.update()
        self._spawn_food()
        self.stats_update_timer += 1
        s_update_interval = STATS_UPDATE_INTERVAL_FRAMES
        if self.stats_update_timer >= s_update_interval:
            self.stats_update_timer = 0
            self._calculate_and_update_stats()
            self._manage_obstacles()

    def render(self):
        fill_c = WHITE if 'WHITE' in globals() else (255,255,255)
        self.screen.fill(fill_c)
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
                if self.plotter.is_graph_showing and self.plotter.fig and \
                   (not hasattr(self.plotter.fig.canvas.manager, 'window') or not self.plotter.fig.canvas.manager.window):
                    self.plotter.close_graph_window() # Ensure state is consistent

                target_fps = FPS if 'FPS' in globals() else 60
                self.clock.tick(target_fps)
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