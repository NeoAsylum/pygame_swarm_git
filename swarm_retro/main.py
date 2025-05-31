import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib import pyplot as plt
import pygame
import random
# import csv # No longer needed if we remove CSV logging entirely

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
        except NameError:
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
        self.frames_to_count_stats = 3 # Graph updates at this interval

        self.num_current_birds = 0
        self.avg_cohesion = 0.0
        self.avg_alignment = 0.0
        self.avg_separation = 0.0
        self.avg_avoidance = 0.0
        self.avg_food_attraction = 0.0

        if not hasattr(Bird, "collision_count"):
            Bird.collision_count = 0

        # --- Data Storage for Graph (In-Memory Lists) ---
        self.graph_time_steps = [] # For the x-axis (data point index)
        self.graph_data = { # For the y-axis data series
            "AvgCohesion": [],
            "AvgAlignment": [],
            "AvgSeparation": [],
            "AvgAvoidance": [],
            "AvgFoodAttraction": [],
        }
        self.data_point_counter = 0 # To generate x-values for the graph

        # --- Matplotlib Graph Setup ---
        self.fig = None
        self.ax = None
        self.plot_lines = {}
        self.is_graph_showing = False # Start with graph closed, or True to start open

        # --- Pygame Button for Graph ---
        button_width = 140
        button_height = (UI_LINE_HEIGHT if 'UI_LINE_HEIGHT' in globals() else 20) + 5
        self.toggle_graph_button_rect = pygame.Rect(
            (SCREEN_WIDTH if 'SCREEN_WIDTH' in globals() else 800) - button_width - (UI_PADDING if 'UI_PADDING' in globals() else 10),
            UI_PADDING if 'UI_PADDING' in globals() else 10,
            button_width, button_height
        )
        self.button_color = (200, 200, 200)
        self.button_hover_color = (230, 230, 230)
        self.button_text_color = BLACK if 'BLACK' in globals() else (0,0,0)

        if self.is_graph_showing:
            self._open_graph_window()

    def _open_graph_window(self):
        if self.fig is not None:
            try: plt.close(self.fig)
            except Exception: pass

        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.plot_lines = {}

        colors = ["blue", "green", "red", "purple", "orange"]
        # These labels must match the keys in self.graph_data
        labels_for_plot = ["AvgCohesion", "AvgAlignment", "AvgSeparation", "AvgAvoidance", "AvgFoodAttraction"]

        self.ax.set_xlabel("Data Point Index")
        self.ax.set_ylabel("Average Strength")
        self.ax.set_title("Flocking Behavior Statistics (In-Memory)")
        self.ax.grid(True)

        for i, label_text in enumerate(labels_for_plot):
            self.plot_lines[label_text], = self.ax.plot([], [], label=label_text, color=colors[i])
        self.ax.legend(loc="upper left")

        self._redraw_all_graph_data() # Plot existing in-memory data

        plt.show(block=False)
        self.is_graph_showing = True
        if self.fig: self.fig.canvas.manager.set_window_title("Flocking Stats Plot (Memory)")

    def _redraw_all_graph_data(self):
        """Plots all current historical data from in-memory lists onto the graph."""
        if not self.is_graph_showing or self.fig is None or self.ax is None:
            return

        max_points_to_show = 200
        current_len_hist = len(self.graph_time_steps)
        start_index_hist = max(0, current_len_hist - max_points_to_show)
        display_time_steps_hist = self.graph_time_steps[start_index_hist:]

        for label_text, line_obj in self.plot_lines.items():
            if label_text in self.graph_data:
                display_data_hist = self.graph_data[label_text][start_index_hist:]
                line_obj.set_data(display_time_steps_hist, display_data_hist)
            else:
                line_obj.set_data([],[]) # Should not happen if keys match

        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except Exception as e:
            print(f"Error redrawing all graph data: {e}")
            self._close_graph_window()

    def _close_graph_window(self):
        if self.fig is not None:
            try: plt.close(self.fig)
            except Exception as e: print(f"Error closing fig: {e}")
        self.fig = None
        self.ax = None
        self.plot_lines = {}
        self.is_graph_showing = False

    def _toggle_graph_window(self):
        if self.is_graph_showing and self.fig is not None:
            self._close_graph_window()
        else:
            self._open_graph_window()

    def _create_initial_birds(self):
        for _ in range(INITIAL_NUM_BIRDS if 'INITIAL_NUM_BIRDS' in globals() else 10):
            bird_x = random.randint(20, SCREEN_WIDTH - 20)
            bird_y = random.randint(20, SCREEN_HEIGHT - 20)
            bird = Bird(bird_x, bird_y)
            self.birds_group.add(bird)

    def _spawn_food(self):
        self.food_spawn_timer += 1
        f_spawn_interval = FOOD_SPAWN_INTERVAL_FRAMES if 'FOOD_SPAWN_INTERVAL_FRAMES' in globals() else 60
        if self.food_spawn_timer >= f_spawn_interval:
            self.food_spawn_timer = 0
            max_food = MAX_FOOD_ON_SCREEN if 'MAX_FOOD_ON_SCREEN' in globals() else 20
            obs_thresh = OBSTACLE_HIGH_BIRD_THRESHOLD if 'OBSTACLE_HIGH_BIRD_THRESHOLD' in globals() else 50
            f_size = FOOD_SIZE if 'FOOD_SIZE' in globals() else 5
            if (len(self.food_group) < max_food or self.num_current_birds < obs_thresh):
                food_x = random.randint(10, SCREEN_WIDTH - 10 - f_size)
                food_y = random.randint(10, SCREEN_HEIGHT - 10 - f_size)
                new_food = Food(food_x, food_y)
                self.food_group.add(new_food)

    def _manage_obstacles(self):
        desired_obs = DESIRED_NUM_OBSTACLES if 'DESIRED_NUM_OBSTACLES' in globals() else 3
        obs_thresh = OBSTACLE_HIGH_BIRD_THRESHOLD if 'OBSTACLE_HIGH_BIRD_THRESHOLD' in globals() else 50
        spawn_condition_met = (
            len(self.obstacle_group) < desired_obs
            or self.num_current_birds > obs_thresh
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

            # Append data to in-memory lists
            self.graph_time_steps.append(self.data_point_counter)
            self.graph_data["AvgCohesion"].append(self.avg_cohesion)
            self.graph_data["AvgAlignment"].append(self.avg_alignment)
            self.graph_data["AvgSeparation"].append(self.avg_separation)
            self.graph_data["AvgAvoidance"].append(self.avg_avoidance)
            self.graph_data["AvgFoodAttraction"].append(self.avg_food_attraction)
            
            if self.is_graph_showing:
                self._update_plot_with_new_data() # Update graph from these lists
            self.data_point_counter += 1

    def _update_plot_with_new_data(self):
        """Updates the Matplotlib graph with the latest data point from in-memory lists."""
        if not self.is_graph_showing or self.fig is None or not self.fig.canvas.manager.window:
            return

        max_points_to_show = 200 # How many of the latest points to display
        current_len = len(self.graph_time_steps)
        start_index = max(0, current_len - max_points_to_show)
        
        display_time_steps = self.graph_time_steps[start_index:]
        for label, line_obj in self.plot_lines.items():
            display_data = self.graph_data[label][start_index:]
            line_obj.set_data(display_time_steps, display_data)

        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except Exception as e:
            print(f"Error updating plot: {e}")
            self._close_graph_window()

    def _render_text(self, text_str, position, color=None, font_obj=None):
        use_font = font_obj if font_obj else self.font
        default_color = BLACK if "BLACK" in globals() else (0, 0, 0)
        text_surface = use_font.render(text_str, True, color if color else default_color)
        self.screen.blit(text_surface, position)

    def _draw_ui(self):
        current_fps_val = int(self.clock.get_fps())
        pad = UI_PADDING if 'UI_PADDING' in globals() else 10
        line_h = UI_LINE_HEIGHT if 'UI_LINE_HEIGHT' in globals() else 20
        stats_y_start = pad + line_h * 2

        self._render_text(f"FPS: {current_fps_val}", (pad, pad))
        self._render_text(f"Bird Count: {self.num_current_birds}", (pad, stats_y_start))
        stats_y_start += line_h

        mouse_pos = pygame.mouse.get_pos()
        current_button_color = self.button_hover_color if self.toggle_graph_button_rect.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.screen, current_button_color, self.toggle_graph_button_rect)
        pygame.draw.rect(self.screen, self.button_text_color, self.toggle_graph_button_rect, 1) 

        button_text_str = "Graph: ON" if self.is_graph_showing and self.fig else "Graph: OFF"
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
                        self._toggle_graph_window()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: 
                    self._toggle_graph_window()

    def update_state(self):
        self.birds_group.update(self.birds_group, self.obstacle_group, self.food_group)
        self.obstacle_group.update()
        self._spawn_food()
        self.stats_update_timer += 1
        s_update_interval = STATS_UPDATE_INTERVAL_FRAMES if 'STATS_UPDATE_INTERVAL_FRAMES' in globals() else 1
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

                target_fps = FPS if 'FPS' in globals() else 60
                self.clock.tick(target_fps)
        except Exception as e:
            print(f"An critical error occurred during the game loop: {e}")
            self.running = False
        finally:
            # No CSV file to close in this version
            self._close_graph_window()
            print("Matplotlib graph resources cleaned up.")

# Main execution block
if __name__ == "__main__":

    game = Game()
    game.run()
    pygame.quit()