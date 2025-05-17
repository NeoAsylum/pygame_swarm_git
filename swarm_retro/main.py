import pygame
import random

from Bird_class import Bird
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
num_birds = 50
birds = []
for _ in range(num_birds):
    bird_x = random.randint(20, width - 20)
    bird_y = random.randint(20, height - 20)
    birds.append(Bird(bird_x, bird_y, width, height))

# --- Obstacle Settings ---
DESIRED_NUM_OBSTACLES = 8
OBSTACLE_WIDTH = 30  # Define a width for obstacles
OBSTACLE_HEIGHT = 30  # Define a height for obstacles
OBSTACLE_SPEED = 4  # Define a speed for obstacles (pixels per frame)
obstacle_frame_counter = 0

# Pygame clock for controlling frame rate
clock = pygame.time.Clock()
fps = 120  # You can set your desired frame rate here


birds_group = pygame.sprite.Group(birds)
obstacle_group = pygame.sprite.Group()
food_group = pygame.sprite.Group()

# Food spawning variables
food_spawn_timer = 0
food_spawn_interval = 2  # Spawn food every 2 frames
max_food_on_screen = 30  # Optional: limit the maximum number of food items


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
    if len(obstacle_group) < DESIRED_NUM_OBSTACLES or num_current_birds > 120:
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


num_current_birds = 0

avg_cohesion = 0
avg_alignment = 0
avg_separation = 0
avg_avoidance = 0
avg_food_attraction = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    spawn_food()

    birds_group.update(
        birds_group, obstacle_group, food_group
    )  # Birds now use spatial partitioning
    obstacle_group.update()
    obstacle_frame_counter += 1
    if obstacle_frame_counter >= 30:
        obstacle_frame_counter = 0
        # --- Calculate and Display Statistics ---
        current_bird_sprites = birds_group.sprites()
        num_current_birds = len(current_bird_sprites)
        if num_current_birds > 0:
            total_cohesion = 0
            total_alignment = 0
            total_separation = 0
            total_avoidance = 0
            total_food_attraction = 0
            for bird_sprite in current_bird_sprites:
                total_cohesion += bird_sprite.cohesion_strength
                total_alignment += bird_sprite.alignment_strength
                total_separation += bird_sprite.separation_strength
                total_avoidance += bird_sprite.avoidance_strength
                total_food_attraction += bird_sprite.food_attraction_strength

            avg_cohesion = total_cohesion / num_current_birds
            avg_alignment = total_alignment / num_current_birds
            avg_separation = total_separation / num_current_birds
            avg_avoidance = total_avoidance / num_current_birds
            avg_food_attraction = total_food_attraction / num_current_birds
        else:
            avg_cohesion = 0
            avg_alignment = 0
            avg_separation = 0
            avg_avoidance = 0
            avg_food_attraction = 0

        manage_obstacles()
    birds_group.draw(screen)
    obstacle_group.draw(screen)
    food_group.draw(screen)  # Draw the food items

    collision_text = font.render(
        f"Collision-score: {Bird.collision_count}", True, (0, 0, 0)
    )
    screen.blit(collision_text, (10, 50))

    current_fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(current_fps)}", True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))
    # Display new stats
    stats_y_start = 80  # Starting Y position for the new stats
    line_height = 30  # Gap between lines of text

    bird_count_surface = font.render(
        f"Bird Count: {num_current_birds}", True, (0, 0, 0)
    )
    screen.blit(bird_count_surface, (10, stats_y_start))

    avg_cohesion_surface = font.render(
        f"Avg Cohesion: {avg_cohesion:.3f}", True, (0, 0, 0)
    )
    screen.blit(avg_cohesion_surface, (10, stats_y_start + line_height))

    avg_alignment_surface = font.render(
        f"Avg Alignment: {avg_alignment:.3f}", True, (0, 0, 0)
    )
    screen.blit(avg_alignment_surface, (10, stats_y_start + 2 * line_height))

    avg_separation_surface = font.render(
        f"Avg Separation: {avg_separation:.3f}", True, (0, 0, 0)
    )
    screen.blit(avg_separation_surface, (10, stats_y_start + 3 * line_height))

    avg_avoidance_surface = font.render(
        f"Avg Avoidance: {avg_avoidance:.3f}", True, (0, 0, 0)
    )
    screen.blit(avg_avoidance_surface, (10, stats_y_start + 4 * line_height))

    avg_food_attraction_surface = font.render(
        f"Avg Food Attraction: {avg_food_attraction:.3f}", True, (0, 0, 0)
    )
    screen.blit(avg_food_attraction_surface, (10, stats_y_start + 5 * line_height))

    # --- End Statistics Display ---

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
