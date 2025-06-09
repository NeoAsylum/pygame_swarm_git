import os
from Plotter import GamePlotter
import pygame
import random
from BirdClass import Bird
from Obstacles import Obstacle
from FoodClass import Food
from ENV import *

class Game:
    def __init__(self):
        pygame.init()
        window_pos_x = 50
        window_pos_y = 50
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{window_pos_x},{window_pos_y}"

        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        pygame.display.set_caption("Genetic Swarm Simulation")
        pygame.display.set_icon(pygame.image.load("icon.jpg"))

        self.font = pygame.font.Font(None, UI_FONT_SIZE)
        self.button_font = pygame.font.Font(None, UI_FONT_SIZE - 4)

        self.menu_active = False
        self.settings = self._load_initial_settings()
        self.setting_ui_elements = {}
        self.menu_font = pygame.font.Font(None, 28)
        self.menu_item_font = pygame.font.Font(None, 24)
        self._setup_menu_ui_elements()

        self.open_menu_button_rect = pygame.Rect(
            SCREEN_WIDTH - 140 - UI_PADDING,
            UI_PADDING + UI_LINE_HEIGHT + 10,
            140,
            UI_LINE_HEIGHT + 5,
        )

        self.clock = pygame.time.Clock()
        self.running = True

        self.birds_group = pygame.sprite.Group()
        self.obstacle_group = pygame.sprite.Group()
        self.food_group = pygame.sprite.Group()
        self._create_initial_birds(self.settings["INITIAL_NUM_BIRDS"])

        self.food_spawn_timer = 0
        self.stats_update_timer = 0
        self.frame_counter_for_logging_stats = 0

        self.num_current_birds = 0

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

        self.plotter = GamePlotter()

        self.toggle_graph_button_rect = pygame.Rect(
            SCREEN_WIDTH - 140 - UI_PADDING,
            UI_PADDING,
            140,
            UI_LINE_HEIGHT + 5,
        )
        self.button_color = (100, 150, 200)
        self.button_hover_color = (120, 170, 220)
        self.button_text_color = WHITE

    def _load_initial_settings(self):
        return {
            "INITIAL_NUM_BIRDS": INITIAL_NUM_BIRDS,
            "FPS": FPS,
            "DESIRED_NUM_OBSTACLES": DESIRED_NUM_OBSTACLES,
            "OBSTACLE_SPEED": OBSTACLE_SPEED,
            "FOOD_SPAWN_INTERVAL_FRAMES": FOOD_SPAWN_INTERVAL_FRAMES,
            "MAX_FOOD_ON_SCREEN": MAX_FOOD_ON_SCREEN,
            "GLOBAL_SPEED_FACTOR": GLOBAL_SPEED_FACTOR,
            "REPRODUCTION_THRESHOLD": REPRODUCTION_THRESHOLD,
            "NUM_FLOCK_NEIGHBORS": NUM_FLOCK_NEIGHBORS,
        }

    def _setup_menu_ui_elements(self):
        self.menu_layout_config = {
            "INITIAL_NUM_BIRDS": {
                "label": "Initial Birds",
                "min": 1,
                "max": 200,
                "step": 1,
                "type": int,
            },
            "FPS": {"label": "FPS", "min": 10, "max": 240, "step": 1, "type": int},
            "DESIRED_NUM_OBSTACLES": {
                "label": "Desired Obstacles",
                "min": 0,
                "max": 50,
                "step": 1,
                "type": int,
            },
            "OBSTACLE_SPEED": {
                "label": "Obstacle Speed",
                "min": 1,
                "max": 20,
                "step": 0.5,
                "type": float,
            },
            "FOOD_SPAWN_INTERVAL_FRAMES": {
                "label": "Food Spawn Interval (frames)",
                "min": 1,
                "max": 300,
                "step": 1,
                "type": int,
            },
            "MAX_FOOD_ON_SCREEN": {
                "label": "Max Food",
                "min": 1,
                "max": 300,
                "step": 1,
                "type": int,
            },
            "GLOBAL_SPEED_FACTOR": {
                "label": "Global Speed Factor",
                "min": 0.1,
                "max": 5.0,
                "step": 0.1,
                "type": float,
            },
            "REPRODUCTION_THRESHOLD": {
                "label": "Reproduction Threshold",
                "min": 1,
                "max": 10,
                "step": 1,
                "type": int,
            },
            "NUM_FLOCK_NEIGHBORS": {
                "label": "Flock Neighbors",
                "min": 1,
                "max": 20,
                "step": 1,
                "type": int,
            },
        }
        self.apply_settings_button_rect = None
        self.close_menu_button_rect = None

    def _create_initial_birds(self, count):
        self.birds_group.empty()
        for _ in range(int(count)):
            bird_x = random.randint(20, SCREEN_WIDTH - 20)
            bird_y = random.randint(20, SCREEN_HEIGHT - 20)
            bird = Bird(bird_x, bird_y, settings=self.settings)
            self.birds_group.add(bird)
        self.num_current_birds = len(self.birds_group)

    def _spawn_food(self):
        self.food_spawn_timer += 1
        if self.food_spawn_timer >= self.settings["FOOD_SPAWN_INTERVAL_FRAMES"]:
            self.food_spawn_timer = 0
            if len(self.food_group) < self.settings["MAX_FOOD_ON_SCREEN"]:
                self.food_group.add(
                    Food(
                        random.randint(10, SCREEN_WIDTH - 10 - FOOD_SIZE),
                        random.randint(10, SCREEN_HEIGHT - 10 - FOOD_SIZE),
                    )
                )

    def _manage_obstacles(self):
        if self.num_current_birds > OBSTACLE_HIGH_BIRD_THRESHOLD:
            how_many_too_many = int(
                round((self.num_current_birds - OBSTACLE_HIGH_BIRD_THRESHOLD) / 10, 0)
            )
            for _ in range(how_many_too_many):
                new_obstacle = Obstacle(speed_x=self.settings["OBSTACLE_SPEED"])
                self.obstacle_group.add(new_obstacle)
        else:
            if len(self.obstacle_group) < self.settings["DESIRED_NUM_OBSTACLES"]:
                new_obstacle = Obstacle(speed_x=self.settings["OBSTACLE_SPEED"])
                self.obstacle_group.add(new_obstacle)

    def _calculate_average_stat(
        self, sprites, attribute_name, num_sprites, default_value=0.0
    ):
        if num_sprites == 0:
            return default_value
        return (
            sum(getattr(b, attribute_name, default_value) for b in sprites)
            / num_sprites
        )

    def _calculate_and_update_stats(self):
        current_bird_sprites = self.birds_group.sprites()
        self.num_current_birds = len(current_bird_sprites)

        if self.num_current_birds > 0:
            self.avg_cohesion = self._calculate_average_stat(
                current_bird_sprites, "cohesion_strength", self.num_current_birds
            )
            self.avg_alignment = self._calculate_average_stat(
                current_bird_sprites, "alignment_strength", self.num_current_birds
            )
            self.avg_separation = self._calculate_average_stat(
                current_bird_sprites, "separation_strength", self.num_current_birds
            )
            self.avg_avoidance = self._calculate_average_stat(
                current_bird_sprites, "avoidance_strength", self.num_current_birds
            )
            self.avg_food_attraction = self._calculate_average_stat(
                current_bird_sprites, "food_attraction_strength", self.num_current_birds
            )
            self.avg_obstacle_avoidance_distance = self._calculate_average_stat(
                current_bird_sprites,
                "obstacle_avoidance_distance",
                self.num_current_birds,
            )
        else:
            self.avg_cohesion = self.avg_alignment = self.avg_separation = (
                self.avg_avoidance
            ) = self.avg_food_attraction = self.avg_obstacle_avoidance_distance = 0.0

        self.frame_counter_for_logging_stats += 1
        if (
            self.frame_counter_for_logging_stats
            >= GRAPH_DATA_LOG_INTERVAL_FRAMES / GAME_LOGIC_UPDATE_INTERVAL_FRAMES
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
                self.plotter.queue_new_plot_data(self.graph_time_steps, self.graph_data)
            self.data_point_counter += 1

    def _render_text(self, text_str, position, font_obj=None):
        use_font = font_obj if font_obj else self.font
        text_surface = use_font.render(text_str, True, BLACK)
        self.screen.blit(text_surface, position)

    def _draw_button(
        self,
        rect,
        text_content,
        base_color,
        hover_color,
        text_color,
        mouse_pos,
        font=None,
    ):
        current_font = font if font else self.button_font
        button_color = hover_color if rect.collidepoint(mouse_pos) else base_color

        pygame.draw.rect(self.screen, button_color, rect)
        pygame.draw.rect(self.screen, text_color, rect, 1)  # Border

        text_surf = current_font.render(text_content, True, text_color)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def _draw_ui(self):
        current_fps_val = int(self.clock.get_fps())
        pad = UI_PADDING
        line_h = UI_LINE_HEIGHT

        self._render_text(f"FPS: {current_fps_val}", (pad, pad))
        self._render_text(f"Bird Count: {self.num_current_birds}", (pad, pad + line_h))
        mouse_pos = pygame.mouse.get_pos()

        graph_button_text = (
            "Graph: ON"
            if self.plotter.is_graph_showing and self.plotter.fig
            else "Graph: OFF"
        )
        self._draw_button(
            self.toggle_graph_button_rect,
            graph_button_text,
            self.button_color,
            self.button_hover_color,
            self.button_text_color,
            mouse_pos,
        )

        self._draw_button(
            self.open_menu_button_rect,
            "Settings Menu",
            self.button_color,
            self.button_hover_color,
            self.button_text_color,
            mouse_pos,
        )

    def _draw_setting_item(
        self,
        surface,
        key_name,
        config,
        current_y_pos,
        overlay_x_pos,
        overlay_y_pos,
        item_h,
        btn_w,
        val_display_w,
        item_padding,
    ):
        label_surf = self.menu_item_font.render(f"{config['label']}:", True, WHITE)
        surface.blit(label_surf, (item_padding, current_y_pos))

        value_str = (
            f"{self.settings[key_name]:.1f}"
            if config["type"] == float
            else str(self.settings[key_name])
        )
        value_surf = self.menu_item_font.render(value_str, True, WHITE)
        value_x_pos = item_padding + label_surf.get_width() + 100
        surface.blit(value_surf, (value_x_pos, current_y_pos))

        minus_rect_local = pygame.Rect(
            value_x_pos + val_display_w, current_y_pos, btn_w, item_h - 5
        )
        pygame.draw.rect(surface, (200, 0, 0), minus_rect_local)
        minus_text = self.menu_font.render("-", True, WHITE)
        surface.blit(minus_text, minus_text.get_rect(center=minus_rect_local.center))

        plus_rect_local = pygame.Rect(
            minus_rect_local.right + 10, current_y_pos, btn_w, item_h - 5
        )
        pygame.draw.rect(surface, (0, 200, 0), plus_rect_local)
        plus_text = self.menu_font.render("+", True, WHITE)
        surface.blit(plus_text, plus_text.get_rect(center=plus_rect_local.center))

        self.setting_ui_elements[key_name] = {
            "minus_rect": minus_rect_local.move(overlay_x_pos, overlay_y_pos),
            "plus_rect": plus_rect_local.move(overlay_x_pos, overlay_y_pos),
            "config": config,
        }

    def _draw_menu_overlay(self):
        if not self.menu_active:
            return

        overlay_width = SCREEN_WIDTH * 0.6
        overlay_height = SCREEN_HEIGHT * 0.8
        overlay_x = (SCREEN_WIDTH - overlay_width) / 2
        overlay_y = (SCREEN_HEIGHT - overlay_height) / 2

        overlay_surface = pygame.Surface(
            (overlay_width, overlay_height), pygame.SRCALPHA
        )
        overlay_surface.fill((50, 50, 50, 220))
        pygame.draw.rect(overlay_surface, WHITE, overlay_surface.get_rect(), 2)

        title_surf = self.font.render("Settings", True, WHITE)
        overlay_surface.blit(
            title_surf, (overlay_width / 2 - title_surf.get_width() / 2, 20)
        )

        current_y = 80
        item_height = 35
        padding = 20
        button_width = 30
        value_display_width = 80

        self.setting_ui_elements.clear()

        for key, config in self.menu_layout_config.items():
            if key not in self.settings:
                continue
            self._draw_setting_item(
                overlay_surface,
                key,
                config,
                current_y,
                overlay_x,
                overlay_y,
                item_height,
                button_width,
                value_display_width,
                padding,
            )
            current_y += item_height + 10

        self.screen.blit(overlay_surface, (overlay_x, overlay_y))

        apply_btn_width = 220
        apply_btn_height = 40
        self.apply_settings_button_rect = pygame.Rect(
            overlay_x + padding,
            overlay_y + overlay_height - apply_btn_height - padding,
            apply_btn_width,
            apply_btn_height,
        )
        self._draw_button(
            self.apply_settings_button_rect,
            "Apply & Respawn Birds",
            (0, 150, 0),
            (0, 180, 0),
            WHITE,
            pygame.mouse.get_pos(),
            self.button_font,
        )

        close_btn_width = 120
        self.close_menu_button_rect = pygame.Rect(
            overlay_x + overlay_width - close_btn_width - padding,
            overlay_y + overlay_height - apply_btn_height - padding,
            close_btn_width,
            apply_btn_height,
        )
        self._draw_button(
            self.close_menu_button_rect,
            "Close Menu",
            (150, 0, 0),
            (180, 0, 0),
            WHITE,
            pygame.mouse.get_pos(),
            self.button_font,
        )

    def _handle_menu_input(self, event):
        if (
            not self.menu_active
            or event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
        ):
            return

        mouse_pos = event.pos
        for key, ui_data in self.setting_ui_elements.items():
            config = ui_data["config"]
            current_value = self.settings[key]
            new_value = current_value

            if ui_data["minus_rect"].collidepoint(mouse_pos):
                new_value = max(config["min"], current_value - config["step"])
            elif ui_data["plus_rect"].collidepoint(mouse_pos):
                new_value = min(config["max"], current_value + config["step"])

            if new_value != current_value:
                self.settings[key] = (
                    config["type"](new_value)
                    if config["type"] == int
                    else round(new_value, 2)
                )
                if key == "FPS":
                    pass

        if (
            self.apply_settings_button_rect
            and self.apply_settings_button_rect.collidepoint(mouse_pos)
        ):
            self._apply_all_settings()
            self.menu_active = False

        if self.close_menu_button_rect and self.close_menu_button_rect.collidepoint(
            mouse_pos
        ):
            self.menu_active = False

    def _apply_all_settings(self):
        print("Applying settings...")
        self._create_initial_birds(self.settings["INITIAL_NUM_BIRDS"])
        print(f"Birds re-created with count: {self.settings['INITIAL_NUM_BIRDS']}")

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.menu_active:
                self._handle_menu_input(event)
            else:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.toggle_graph_button_rect.collidepoint(event.pos):
                            self.plotter.toggle_graph_window(
                                self.graph_time_steps, self.graph_data
                            )
                        elif self.open_menu_button_rect.collidepoint(event.pos):
                            self.menu_active = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        self.plotter.toggle_graph_window(
                            self.graph_time_steps, self.graph_data
                        )
                    elif event.key == pygame.K_ESCAPE and self.menu_active:
                        self.menu_active = False

    def update_state(self):
        self.birds_group.update(self.birds_group, self.obstacle_group, self.food_group)
        self.obstacle_group.update()
        self._spawn_food()
        self.stats_update_timer += 1
        if self.stats_update_timer >= GAME_LOGIC_UPDATE_INTERVAL_FRAMES:
            self.stats_update_timer = 0
            self._calculate_and_update_stats()
            self._manage_obstacles()

    def render(self):
        self.screen.fill(SKY_BLUE)
        self.birds_group.draw(self.screen)
        self.obstacle_group.draw(self.screen)
        for obstacle in self.obstacle_group:  # Draw lingering particles
            if hasattr(obstacle, "draw_trail_particles"):
                obstacle.draw_trail_particles(self.screen)
        self.food_group.draw(self.screen)
        self._draw_ui()
        if self.menu_active:
            self._draw_menu_overlay()
        pygame.display.flip()

    def run(self):
        try:
            while self.running:
                self.process_events()
                if not self.menu_active:
                    self.update_state()
                self.render()

                if self.plotter.is_graph_showing:
                    if not self.plotter.is_window_alive():
                        self.plotter.close_graph_window()

                self.clock.tick(self.settings["FPS"])
        except Exception as e:
            print(f"An critical error occurred during the game loop: {e}")
            import traceback

            traceback.print_exc()
            self.running = False
        finally:
            if self.plotter: # Check if plotter was initialized
                self.plotter.close_graph_window() # This will also stop the thread
                print("Matplotlib graph resources cleaned up.")
            pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
