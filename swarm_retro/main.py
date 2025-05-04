import pygame
import random

from Bird_class import Bird
from SliderManagerClass import SliderManager
from SpatialGridClass import SpatialGrid
from Obstacles import Obstacle

# Initialize Pygame
pygame.init()
# Screen dimensions
width = 1800
height = 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flocking Birds - Buttons")
font = pygame.font.Font(None, 30)

# Create a list of birds
num_birds = 400
birds = []
for _ in range(num_birds):
    bird_x = random.randint(20, width - 20)
    bird_y = random.randint(20, height - 20)
    birds.append(Bird(bird_x, bird_y, width, height))
num_obstacles = 10
obstacles = []
for _ in range(num_obstacles):
    obstacle_x = random.randint(20, width - 20)
    obstacle_y = random.randint(20, height - 20)
    obstacles.append(Obstacle(obstacle_x, obstacle_y, 20, 20))

# Pygame clock for controlling frame rate
clock = pygame.time.Clock()
fps = 200  # You can set your desired frame rate here

# Initialize sliders
slider_manager = SliderManager(screen, height)
slider_manager.apply_values_to_birds(birds)

birds_group = pygame.sprite.Group(birds)
obstacle_group = pygame.sprite.Group(obstacles)

# Initialize spatial grid
spatial_grid = SpatialGrid(width, height)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif slider_manager.handle_event(event) == "apply":
            slider_manager.apply_values_to_birds(birds)

    screen.fill((255, 255, 255))

    spatial_grid.clear()  # Reset grid every frame
    for bird in birds:
        spatial_grid.add_bird(bird)  # Assign birds to grid cells

    birds_group.update(
        spatial_grid, obstacle_group
    )  # Birds now use spatial partitioning
    obstacle_group.update()
    birds_group.draw(screen)
    obstacle_group.draw(screen)

    slider_manager.draw_sliders()

    collision_text = font.render(f"Collision-score: {Bird.collision_count}", True, (0, 0, 0))
    screen.blit(collision_text, (10, 50))  # Display collision count

    current_fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(current_fps)}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
