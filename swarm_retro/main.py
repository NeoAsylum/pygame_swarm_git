# pygame_swarm_git/swarm_retro/main.py
import pygame
import random
import sys # Für sys.exit (optional, aber sauberer)

from Bird_class import Bird
from SliderManagerClass import SliderManager
from SpatialGridClass import SpatialGrid
from Obstacles import CometObstacle
from Food import Food
import config_retro as cfg

pygame.init()
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("Flocking Birds Evolved - Predictive Avoidance")
font = pygame.font.Font(None, 30)

all_sprites = pygame.sprite.Group()
birds_group = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()
food_group = pygame.sprite.Group()

birds_list = []
for _ in range(cfg.INITIAL_BIRDS):
    bird_x = random.randint(20, cfg.WIDTH - 20)
    bird_y = random.randint(20, cfg.HEIGHT - 20)
    new_bird = Bird(bird_x, bird_y, cfg.WIDTH, cfg.HEIGHT,
                    # Startwerte für Flocking etc. kommen aus cfg
                    cohesion_strength=cfg.DEFAULT_COHESION,
                    alignment_strength=cfg.DEFAULT_ALIGNMENT,
                    separation_strength=cfg.DEFAULT_SEPARATION,
                    global_speed_factor=cfg.DEFAULT_SPEED,
                    slider_avoidance_strength=cfg.DEFAULT_AVOIDANCE_SLIDER)
    birds_list.append(new_bird)
    birds_group.add(new_bird)
    all_sprites.add(new_bird)

for _ in range(cfg.INITIAL_COMETS):
    new_comet = CometObstacle()
    obstacle_group.add(new_comet)
    all_sprites.add(new_comet)

food_spawn_timer = 0
comet_spawn_timer = 0

def spawn_food_item():
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
# Die Vögel erhalten ihre Startwerte für Slider-abhängige Parameter
# (global_speed_factor, slider_avoidance_strength) bereits im Konstruktor
# über die cfg.DEFAULT_ Werte.
# Der "Apply" Button synchronisiert dann alle Vögel mit den aktuellen Slider-Positionen.

spatial_grid = SpatialGrid(cfg.WIDTH, cfg.HEIGHT, cell_size=100)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        action = slider_manager.handle_event(event)
        if action == "apply":
            # Wende die aktuellen Slider-Werte auf alle Vögel an
            for bird_obj in birds_group:
                bird_obj.cohesion_strength = slider_manager.cohesion_strength
                bird_obj.alignment_strength = slider_manager.alignment_strength
                bird_obj.separation_strength = slider_manager.separation_strength
                bird_obj.global_speed_factor = slider_manager.global_speed_factor
                bird_obj.slider_avoidance_strength = slider_manager.avoidance_strength # Stellt sicher, dass der richtige Vogel-Attributname verwendet wird
        # Der "close" Button wurde entfernt, daher keine Abfrage mehr hier
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                new_comet = CometObstacle(x=mouse_x, y=mouse_y - cfg.COMET_SIZE_H // 2, auto_spawn_from_edge=False)
                obstacle_group.add(new_comet)
                all_sprites.add(new_comet)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                new_comet = CometObstacle()
                obstacle_group.add(new_comet)
                all_sprites.add(new_comet)

    if not running:
        break

    food_spawn_timer += 1
    if food_spawn_timer >= cfg.FOOD_SPAWN_RATE:
        spawn_food_item()
        food_spawn_timer = 0

    comet_spawn_timer += 1
    if comet_spawn_timer >= cfg.COMET_SPAWN_RATE:
        spawn_automatic_comet()
        comet_spawn_timer = 0

    spatial_grid.clear()
    for bird_obj in birds_group:
        spatial_grid.add_bird(bird_obj)

    newly_born_birds = []
    for bird_obj in list(birds_group): # Wichtig: Kopie der Gruppe für sichere Iteration
        if not bird_obj.alive():
            if bird_obj in birds_list: birds_list.remove(bird_obj) # Aus optionaler Liste entfernen
            continue

        offspring = bird_obj.update(spatial_grid, obstacle_group, food_group)
        
        if offspring:
            newly_born_birds.append(offspring)
        
        if not bird_obj.alive(): # Erneut prüfen, da .update() zum Tod führen kann
            if bird_obj in birds_list:
                 birds_list.remove(bird_obj)
            # .kill() entfernt Sprite aus allen Gruppen

    for new_b in newly_born_birds:
        # Optional: Populationslimit, um Überbevölkerung zu vermeiden
        if len(birds_group) < cfg.INITIAL_BIRDS * 3 : # Beispiel: Max 3x Startpopulation
             if new_b not in birds_list: birds_list.append(new_b) # Sicherstellen, dass nicht doppelt hinzugefügt
             birds_group.add(new_b)
             all_sprites.add(new_b)

    obstacle_group.update()
    
    screen.fill(cfg.WHITE)
    all_sprites.draw(screen)
    slider_manager.draw_sliders_and_buttons()

    # UI Texte
    num_birds_text = font.render(f"Birds: {len(birds_group)}", True, cfg.BLACK)
    screen.blit(num_birds_text, (10, 80))

    avg_energy_val = 0
    if len(birds_group) > 0:
        avg_energy_val = sum(b.energy for b in birds_group) / len(birds_group)
    avg_energy_text = font.render(f"Avg Energy: {avg_energy_val:.1f}", True, cfg.BLACK)
    screen.blit(avg_energy_text, (10, 110))

    avg_pred_horizon = 0
    avg_react_strength = 0
    if len(birds_group) > 0:
        avg_pred_horizon = sum(b.prediction_horizon for b in birds_group) / len(birds_group)
        avg_react_strength = sum(b.reaction_strength for b in birds_group) / len(birds_group)
    avg_pred_text = font.render(f"Avg Horizon: {avg_pred_horizon:.1f}", True, cfg.BLACK)
    screen.blit(avg_pred_text, (10, 140))
    avg_react_text = font.render(f"Avg React Str: {avg_react_strength:.2f}", True, cfg.BLACK)
    screen.blit(avg_react_text, (10, 170))


    num_comets_text = font.render(f"Comets: {len(obstacle_group)}", True, cfg.BLACK)
    screen.blit(num_comets_text, (10, 200))
    
    current_fps_val = clock.get_fps()
    fps_text = font.render(f"FPS: {int(current_fps_val)}", True, cfg.BLACK)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(cfg.FPS)

pygame.quit()
sys.exit() # Expliziter Exit