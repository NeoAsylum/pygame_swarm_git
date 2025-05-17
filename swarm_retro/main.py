import pygame
import random

from Bird_class import Bird
from SliderManagerClass import SliderManager
from SpatialGridClass import SpatialGrid
from Obstacles import Obstacle
from FoodClass import Food  # Import the Food class

# Initialize Pygame
pygame.init()
# Screen dimensions
width = 1800
height = 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flocking Birds - Buttons")
font = pygame.font.Font(None, 30)

# Create a list of birds
num_birds = 200
birds = []
for _ in range(num_birds):
    bird_x = random.randint(20, width - 20)
    bird_y = random.randint(20, height - 20)
    birds.append(Bird(bird_x, bird_y, width, height))

# --- Obstacle Settings ---
DESIRED_NUM_OBSTACLES = 10
OBSTACLE_WIDTH = 30  # Define a width for obstacles
OBSTACLE_HEIGHT = 30  # Define a height for obstacles
OBSTACLE_SPEED = 3  # Define a speed for obstacles (pixels per frame)
obstacle_frame_counter = 0

# Pygame clock for controlling frame rate
clock = pygame.time.Clock()
fps = 60  # You can set your desired frame rate here

# Initialize sliders
slider_manager = SliderManager(screen, height)
slider_manager.apply_values_to_birds(birds)

birds_group = pygame.sprite.Group(birds)
obstacle_group = pygame.sprite.Group()
food_group = pygame.sprite.Group()

# Food spawning variables
food_spawn_timer = 0
food_spawn_interval = 2  # Spawn food every 2 frames
max_food_on_screen = 100  # Optional: limit the maximum number of food items


def spawn_food():
    global food_spawn_timer  # Declare that you are using the global variable
    food_spawn_timer += 1
    if food_spawn_timer >= food_spawn_interval:
        food_spawn_timer = 0  # Reset timer
        # Optional: Only spawn if below max_food_on_screen
        if len(food_group) < max_food_on_screen:
            food_x = random.randint(10, width - 10)  # Ensure food is fully on screen
            food_y = random.randint(10, height - 10)
            # Assuming food items are 10x10 pixels, adjust if your Food class has different dimensions
            new_food = Food(food_x, food_y, 10, 10)
            food_group.add(new_food)


def manage_obstacles():
    """
    Ensures there are always DESIRED_NUM_OBSTACLES on screen.
    Spawns at most one new obstacle per frame if the count is below desired.
    """
    # If the number of obstacles is less than desired, spawn ONE new obstacle
    if len(obstacle_group) < DESIRED_NUM_OBSTACLES:
        # Spawn at the right edge of the screen
        spawn_x = width  # Start at the right edge
        # Spawn at a random vertical position
        spawn_y = random.randint(
            0, height - OBSTACLE_HEIGHT
        )  # Ensure fully on screen vertically

        new_obstacle = Obstacle(
            spawn_x, spawn_y, OBSTACLE_WIDTH, OBSTACLE_HEIGHT, OBSTACLE_SPEED
        )
        obstacle_group.add(new_obstacle)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif slider_manager.handle_event(event) == "apply":
            slider_manager.apply_values_to_birds(birds)

    screen.fill((255, 255, 255))
    spawn_food()

    birds_group.update(
        birds_group, obstacle_group, food_group
    )  # Birds now use spatial partitioning
    obstacle_group.update()
    obstacle_frame_counter += 1
    if obstacle_frame_counter >= 45:
        obstacle_frame_counter = 0
        manage_obstacles()
    birds_group.draw(screen)
    obstacle_group.draw(screen)
    food_group.draw(screen)  # Draw the food items

    slider_manager.draw_sliders()

    collision_text = font.render(
        f"Collision-score: {Bird.collision_count}", True, (0, 0, 0)
    )
    screen.blit(collision_text, (10, 50))

    current_fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(current_fps)}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
