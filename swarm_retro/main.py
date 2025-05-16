# pygame_swarm_git/swarm_retro/main.py
import pygame
import random
import sys
import csv
import json
import datetime

from Bird_class import Bird # Stellt sicher, dass die Bird-Klasse mit reproduction_count importiert wird
from SliderManagerClass import SliderManager
from SpatialGridClass import SpatialGrid
from Obstacles import CometObstacle
from Food import Food
import config_retro as cfg

pygame.init()
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("Flocking Birds Evolved - Predictive Avoidance & Learning")
font = pygame.font.Font(None, 30)
ui_font_small = pygame.font.Font(None, 24)

all_sprites = pygame.sprite.Group()
birds_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
food_group = pygame.sprite.Group()

# birds_list = [] # Kann für spezifische Analysen beibehalten werden

LOG_FILENAME = f"{cfg.LOG_FILE_BASENAME}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
LOG_INTERVAL_FRAMES = cfg.FPS * cfg.LOG_INTERVAL_SECONDS
log_timer = 0

with open(LOG_FILENAME, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([
        'Timestamp_s', 'Population', 'Avg_Energy',
        'Avg_Cohesion', 'Avg_Alignment', 'Avg_Separation',
        'Avg_Pred_Horizon', 'Avg_React_Strength',
        'Avg_Hunger_Drive', 'Avg_Low_E_Factor',
        'Total_Collisions', 'Total_Reproductions', # NEU: Spalte für Reproduktionen
        'Food_Items'
    ])
Bird.collision_count = 0
Bird.reproduction_count = 0 # NEU: Zähler initialisieren

def spawn_bird_from_data(bird_data):
    new_genes = {
        'cohesion': bird_data['cohesion_strength'],
        'alignment': bird_data['alignment_strength'],
        'separation': bird_data['separation_strength'],
        'prediction_horizon': bird_data['prediction_horizon'],
        'reaction_strength': bird_data['reaction_strength'],
        'hunger_drive_factor': bird_data.get('hunger_drive_factor', cfg.BIRD_HUNGER_DRIVE_FACTOR_DEFAULT),
        'low_energy_threshold_factor': bird_data.get('low_energy_threshold_factor', cfg.BIRD_LOW_ENERGY_THRESHOLD_FACTOR_DEFAULT),
    }
    new_bird = Bird(
        x=bird_data['x'], y=bird_data['y'],
        screen_width=cfg.WIDTH, screen_height=cfg.HEIGHT,
        passed_genes=new_genes,
        global_speed_factor=bird_data.get('global_speed_factor', cfg.DEFAULT_SPEED),
        slider_avoidance_strength=bird_data.get('slider_avoidance_strength', cfg.DEFAULT_AVOIDANCE_SLIDER),
        energy=bird_data['energy']
    )
    birds_group.add(new_bird)
    all_sprites.add(new_bird)
    return new_bird

def save_population_to_file():
    data_to_save = []
    for bird in birds_group:
        data_to_save.append({
            'x': bird.x, 'y': bird.y,
            'speed_x': bird.speed_x, 'speed_y': bird.speed_y,
            'energy': bird.energy,
            'cohesion_strength': bird.cohesion_strength,
            'alignment_strength': bird.alignment_strength,
            'separation_strength': bird.separation_strength,
            'prediction_horizon': bird.prediction_horizon,
            'reaction_strength': bird.reaction_strength,
            'hunger_drive_factor': bird.hunger_drive_factor,
            'low_energy_threshold_factor': bird.low_energy_threshold_factor,
            'global_speed_factor': bird.global_speed_factor,
            'slider_avoidance_strength': bird.slider_avoidance_strength
        })
    try:
        with open(cfg.SAVE_FILENAME, 'w') as f:
            json.dump(data_to_save, f, indent=4)
        print(f"Population saved to {cfg.SAVE_FILENAME}")
    except Exception as e:
        print(f"Error saving population: {e}")

def load_population_from_file():
    for bird_obj in list(birds_group): bird_obj.kill()
    # birds_list.clear()

    try:
        with open(cfg.SAVE_FILENAME, 'r') as f:
            loaded_data = json.load(f)
        for bird_data in loaded_data:
            spawn_bird_from_data(bird_data)
        print(f"Population loaded from {cfg.SAVE_FILENAME}")
    except FileNotFoundError:
        print(f"Save file {cfg.SAVE_FILENAME} not found.")
    except Exception as e:
        print(f"Error loading population: {e}")

for _ in range(cfg.INITIAL_BIRDS):
    bird_x = random.randint(20, cfg.WIDTH - 20)
    bird_y = random.randint(20, cfg.HEIGHT - 20)
    new_bird = Bird(bird_x, bird_y, cfg.WIDTH, cfg.HEIGHT)
    # birds_list.append(new_bird)
    birds_group.add(new_bird)
    all_sprites.add(new_bird)

for _ in range(cfg.INITIAL_COMETS):
    new_comet = CometObstacle()
    obstacle_group.add(new_comet)
    all_sprites.add(new_comet)

food_spawn_timer = 0
comet_spawn_timer = 0
current_comet_spawn_rate = cfg.COMET_SPAWN_RATE
current_food_spawn_rate = cfg.FOOD_SPAWN_RATE

def spawn_food_item(count=1):
    for _ in range(count):
        if len(food_group) < cfg.MAX_FOOD_ITEMS:
            food_x = random.randint(20, cfg.WIDTH - 20)
            food_y = random.randint(20, cfg.HEIGHT - 20)
            new_food = Food(food_x, food_y)
            food_group.add(new_food)
            all_sprites.add(new_food)

def spawn_automatic_comet():
    if len(obstacle_group) < cfg.MAX_COMETS_ON_SCREEN:
        new_comet = CometObstacle()
        obstacle_group.add(new_comet)
        all_sprites.add(new_comet)

clock = pygame.time.Clock()
slider_manager = SliderManager(screen, cfg.HEIGHT)
spatial_grid = SpatialGrid(cfg.WIDTH, cfg.HEIGHT, cell_size=100)

running = True
simulation_time_seconds = 0

while running:
    simulation_time_seconds += 1 / cfg.FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        action = slider_manager.handle_event(event)
        if action == "apply":
            for bird_obj in birds_group:
                bird_obj.cohesion_strength = slider_manager.cohesion_strength
                bird_obj.alignment_strength = slider_manager.alignment_strength
                bird_obj.separation_strength = slider_manager.separation_strength
                bird_obj.global_speed_factor = slider_manager.global_speed_factor
                bird_obj.slider_avoidance_strength = slider_manager.avoidance_strength
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            is_over_slider_ui = False
            if slider_manager.apply_button_rect.collidepoint(event.pos):
                is_over_slider_ui = True
            else:
                for name, (rect, attr_name) in slider_manager.get_slider_rects_and_attributes().items():
                    if rect.collidepoint(event.pos):
                        is_over_slider_ui = True
                        break
            if event.button == 1 and not is_over_slider_ui:
                mouse_x, mouse_y = event.pos
                new_comet = CometObstacle(x=mouse_x, y=mouse_y - cfg.COMET_SIZE_H // 2, auto_spawn_from_edge=False)
                obstacle_group.add(new_comet)
                all_sprites.add(new_comet)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                spawn_automatic_comet()
            if event.key == pygame.K_s:
                save_population_to_file()
            if event.key == pygame.K_l:
                load_population_from_file()
            if event.key == pygame.K_f:
                spawn_food_item(count=cfg.FOOD_SPAWN_BURST_AMOUNT)
                print("Food burst spawned!")
            if event.key == pygame.K_UP:
                current_comet_spawn_rate = max(10, current_comet_spawn_rate - cfg.COMET_SPAWN_RATE_INCREMENT)
                print(f"Comet spawn rate decreased to: {current_comet_spawn_rate} frames")
            if event.key == pygame.K_DOWN:
                current_comet_spawn_rate += cfg.COMET_SPAWN_RATE_INCREMENT
                print(f"Comet spawn rate increased to: {current_comet_spawn_rate} frames")

    if not running: break

    food_spawn_timer += 1
    if food_spawn_timer >= current_food_spawn_rate:
        spawn_food_item()
        food_spawn_timer = 0

    comet_spawn_timer += 1
    if comet_spawn_timer >= current_comet_spawn_rate:
        spawn_automatic_comet()
        comet_spawn_timer = 0

    spatial_grid.clear()
    for bird_obj in birds_group:
        if bird_obj.alive():
            spatial_grid.add_bird(bird_obj)

    newly_born_birds = []
    for bird_obj in list(birds_group):
        if not bird_obj.alive():
            continue
        offspring = bird_obj.update(spatial_grid, obstacle_group, food_group)
        if offspring:
            newly_born_birds.append(offspring)

    for new_b in newly_born_birds:
        if len(birds_group) < cfg.INITIAL_BIRDS * 3 :
             birds_group.add(new_b)
             all_sprites.add(new_b)

    obstacle_group.update()
    
    screen.fill(cfg.WHITE)
    all_sprites.draw(screen)
    slider_manager.draw_sliders_and_buttons()

    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, cfg.BLACK)
    screen.blit(fps_text, (10, 10))
    num_birds_text = font.render(f"Birds: {len(birds_group)}", True, cfg.BLACK)
    screen.blit(num_birds_text, (10, 40))
    
    avg_energy_val = 0
    avg_cohesion = 0
    avg_alignment = 0
    avg_separation = 0
    avg_pred_horizon = 0
    avg_react_strength = 0
    avg_hunger_drive = 0
    avg_low_e_factor = 0

    if len(birds_group) > 0:
        num_b = len(birds_group)
        avg_energy_val = sum(b.energy for b in birds_group) / num_b
        avg_cohesion = sum(b.cohesion_strength for b in birds_group) / num_b
        avg_alignment = sum(b.alignment_strength for b in birds_group) / num_b
        avg_separation = sum(b.separation_strength for b in birds_group) / num_b
        avg_pred_horizon = sum(b.prediction_horizon for b in birds_group) / num_b
        avg_react_strength = sum(b.reaction_strength for b in birds_group) / num_b
        avg_hunger_drive = sum(b.hunger_drive_factor for b in birds_group) / num_b
        avg_low_e_factor = sum(b.low_energy_threshold_factor for b in birds_group) / num_b

    y_offset = 70
    line_height = 22

    ui_texts = [
        f"Avg Energy: {avg_energy_val:.1f}",
        f"Avg Cohesion: {avg_cohesion:.2f}",
        f"Avg Alignment: {avg_alignment:.2f}",
        f"Avg Separation: {avg_separation:.2f}",
        f"Avg Horizon: {avg_pred_horizon:.1f}",
        f"Avg React Str: {avg_react_strength:.2f}",
        f"Avg Hunger Dr: {avg_hunger_drive:.2f}",
        f"Avg Low E Fac: {avg_low_e_factor:.2f}",
        f"Comets: {len(obstacle_group)} (Spawn: {current_comet_spawn_rate}f)",
        f"Food: {len(food_group)}",
        f"Collisions: {Bird.collision_count}",
        f"Reproductions: {Bird.reproduction_count}", # NEU: Anzeige Reproduktionen
        f"Time: {simulation_time_seconds:.0f}s"
    ]
    for i, text_content in enumerate(ui_texts):
        text_surface = ui_font_small.render(text_content, True, cfg.BLACK)
        screen.blit(text_surface, (10, y_offset + i * line_height))
    
    log_timer += 1
    if log_timer >= LOG_INTERVAL_FRAMES:
        log_timer = 0
        try:
            with open(LOG_FILENAME, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    f"{simulation_time_seconds:.2f}", len(birds_group), f"{avg_energy_val:.2f}",
                    f"{avg_cohesion:.3f}", f"{avg_alignment:.3f}", f"{avg_separation:.3f}",
                    f"{avg_pred_horizon:.2f}", f"{avg_react_strength:.3f}",
                    f"{avg_hunger_drive:.3f}", f"{avg_low_e_factor:.3f}",
                    Bird.collision_count, Bird.reproduction_count, # NEU: Logging Reproduktionen
                    len(food_group)
                ])
        except Exception as e:
            print(f"Error writing to log file: {e}")

    pygame.display.flip()
    clock.tick(cfg.FPS)

pygame.quit()
sys.exit()