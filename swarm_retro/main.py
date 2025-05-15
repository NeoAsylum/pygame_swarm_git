# pygame_swarm_git/swarm_retro/main.py
import pygame
import random

# Stellen Sie sicher, dass Bird_class.py die korrekte Energie-Logik hat (kein self.energy -= 0.05)
from Bird_class import Bird
from SliderManagerClass import SliderManager # Diese Datei wurde gerade geändert
from SpatialGridClass import SpatialGrid
from Obstacles import CometObstacle
from Food import Food
import config_retro as cfg

pygame.init()
screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
pygame.display.set_caption("Flocking Birds Evolved - Comets & Food")
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
                    cohesion_strength=cfg.DEFAULT_COHESION,
                    alignment_strength=cfg.DEFAULT_ALIGNMENT,
                    separation_strength=cfg.DEFAULT_SEPARATION,
                    global_speed_factor=cfg.DEFAULT_SPEED,
                    avoidance_strength=cfg.DEFAULT_AVOIDANCE)
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
for bird_obj in birds_group: # birds_list kann hier auch verwendet werden
    bird_obj.cohesion_strength = slider_manager.cohesion_strength
    bird_obj.alignment_strength = slider_manager.alignment_strength
    bird_obj.separation_strength = slider_manager.separation_strength
    bird_obj.global_speed_factor = slider_manager.global_speed_factor
    bird_obj.avoidance_strength = slider_manager.avoidance_strength

spatial_grid = SpatialGrid(cfg.WIDTH, cfg.HEIGHT, cell_size=100)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        action = slider_manager.handle_event(event)
        if action == "apply":
            slider_manager.apply_values_to_birds(birds_group)
        # Die Bedingung "elif action == 'close':" wurde entfernt
        
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
    for bird_obj in list(birds_group):
        if not bird_obj.alive():
            if bird_obj in birds_list: birds_list.remove(bird_obj)
            continue

        offspring = bird_obj.update(spatial_grid, obstacle_group, food_group)
        
        if offspring:
            newly_born_birds.append(offspring)
        
        if not bird_obj.alive():
            if bird_obj in birds_list:
                 birds_list.remove(bird_obj)

    for new_b in newly_born_birds:
        if len(birds_group) < 2 * cfg.INITIAL_BIRDS :
             birds_list.append(new_b)
             birds_group.add(new_b)
             all_sprites.add(new_b)

    obstacle_group.update()
    
    screen.fill(cfg.WHITE)
    all_sprites.draw(screen)
    slider_manager.draw_sliders_and_buttons() # Der Methodenname ist hier korrekt

    num_birds_text = font.render(f"Birds: {len(birds_group)}", True, cfg.BLACK)
    screen.blit(num_birds_text, (10, 80))
    avg_energy_val = 0
    if len(birds_group) > 0:
        avg_energy_val = sum(b.energy for b in birds_group) / len(birds_group)
    avg_energy_text = font.render(f"Avg Energy: {avg_energy_val:.1f}", True, cfg.BLACK)
    screen.blit(avg_energy_text, (10, 110))
    num_comets_text = font.render(f"Comets: {len(obstacle_group)}", True, cfg.BLACK)
    screen.blit(num_comets_text, (10, 140))
    current_fps_val = clock.get_fps()
    fps_text = font.render(f"FPS: {int(current_fps_val)}", True, cfg.BLACK)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(cfg.FPS)

pygame.quit()