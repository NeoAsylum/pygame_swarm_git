import heapq
import math
import random
import pygame
from env import *


class Bird(pygame.sprite.Sprite):
    collision_count = 0

    def __init__(
        self,
        x,
        y,
        cohesion_strength=0.1,
        alignment_strength=0.1,
        separation_strength=0.1,
        avoidance_strength=0.1,
        food_attraction_strength=0.1,
        obstacle_avoidance_distance=0.1,
    ):
        super().__init__()
        self.scree_width = SCREEN_WIDTH  # Store screen width
        self.screen_height = SCREEN_HEIGHT  # Store screen height
        self.cohesion_strength = cohesion_strength * random.uniform(0.9, 1.1)
        self.alignment_strength = alignment_strength * random.uniform(0.9, 1.1)
        self.separation_strength = separation_strength * random.uniform(0.9, 1.1)
        self.avoidance_strength = avoidance_strength * random.uniform(0.9, 1.1)
        self.x = x
        self.y = y
        self.obstacle_avoidance_distance = obstacle_avoidance_distance * random.uniform(
            0.9, 1.1
        )

        angle = random.uniform(0, 2 * math.pi)
        self.speed_x = math.cos(angle)
        self.speed_y = math.sin(angle)
        magnitude = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude

        self.radius = DEFAULT_RADIUS
        self.color = (20, 20, 20)
        self.separation_distance = 50 * random.uniform(0.9, 1.1)
        self.food_counter = 0
        self.food_attraction_strength = food_attraction_strength * random.uniform(
            0.9, 1.1
        )  # Store food attraction strength

        # --- Create the Base Image (Triangle pointing right) ---
        # Size for the triangle base image
        base_size = (
            self.radius * 2.5
        )  # Make it slightly larger than diameter for better look
        # Points for a simple triangle pointing right (+X direction)
        # Centered roughly within the surface for better rotation pivot
        # Surface needs to be large enough to hold the rotated shape
        surf_size = int(base_size * 1.5)  # Make surface larger than shape
        center_offset = surf_size / 2

        # Define triangle points relative to surface center (pointing right)
        tip = (center_offset + base_size * 0.6, center_offset)
        wing_top = (center_offset - base_size * 0.4, center_offset - base_size * 0.4)
        wing_bottom = (center_offset - base_size * 0.4, center_offset + base_size * 0.4)

        # Create transparent surface
        self.base_image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        # Draw the triangle
        pygame.draw.polygon(self.base_image, self.color, [tip, wing_top, wing_bottom])

        # Pygame sprite requirements
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.obstacle_found_ahead = False

    def move(self):
        self.x += self.speed_x * GLOBAL_SPEED_FACTOR
        self.y += self.speed_y * GLOBAL_SPEED_FACTOR

        # Instant boundary reversal
        if self.x <= self.radius or self.x >= self.scree_width - self.radius:
            self.speed_x *= -1
        if self.y <= self.radius or self.y >= self.screen_height - self.radius:
            self.speed_y *= -1

        self.x = max(self.radius, min(self.scree_width - self.radius, self.x))
        self.y = max(self.radius, min(self.screen_height - self.radius, self.y))

        self.rect.center = (self.x, self.y)

    def flock(self, closest_birds):
        closest_birds

        # Alignment
        avg_vx = sum(bird.speed_x for bird in closest_birds) / len(closest_birds)
        avg_vy = sum(bird.speed_y for bird in closest_birds) / len(closest_birds)
        alignment_force_x = avg_vx - self.speed_x
        alignment_force_y = avg_vy - self.speed_y
        self.apply_new_velocity(
            alignment_force_x, alignment_force_y, self.alignment_strength
        )

        # Cohesion
        avg_x = sum(bird.x for bird in closest_birds) / len(closest_birds)
        avg_y = sum(bird.y for bird in closest_birds) / len(closest_birds)
        cohesion_force_x = (avg_x - self.x) / 10
        cohesion_force_y = (avg_y - self.y) / 10
        self.apply_new_velocity(
            cohesion_force_x, cohesion_force_y, self.cohesion_strength
        )

        # Separation
        separation_force_x = 0
        separation_force_y = 0
        epsilon = 0.00001
        for other in closest_birds:
            distance = (self.x - other.x) ** 2 + (self.y - other.y) ** 2
            if distance < self.separation_distance:
                diff_x = self.x - other.x
                diff_y = self.y - other.y
                force = 300 / (distance + epsilon)
                separation_force_x += diff_x * force
                separation_force_y += diff_y * force
        self.apply_new_velocity(
            separation_force_x, separation_force_y, self.separation_strength / 15
        )

    def apply_new_velocity(self, force_x, force_y, weight):
        self.speed_x += force_x * weight * 0.027
        self.speed_y += force_y * weight * 0.027

        magnitude = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude

    def avoid_obstacles(self, obstacles_group):
        """
        Simplified obstacle avoidance for horizontally moving obstacles.
        Relies on direct X-axis proximity and Y-axis overlap, no cone of vision.
        """

        HORIZONTAL_REACTION_DISTANCE = 200  # pixels: How close horizontally (on x-axis)
        # an obstacle needs to be to be considered.

        # Check if the obstacle is horizontally relevant
        # (e.g., its right edge is past the bird's left, and
        #  its left edge is not too far past the bird's right + reaction distance)

        accumulated_vertical_force_component = 0
        self.obstacle_found_ahead = (
            False  # Flag to indicate if any avoidance action was taken
        )
        # Base magnitude for the vertical evasion force component.
        # This will be scaled by self.avoidance_strength in apply_new_velocity.
        VERTICAL_EVASION_MAGNITUDE = 1.5
        for obstacle in obstacles_group:
            is_horizontally_close = (
                obstacle.rect.right > self.rect.left
                and obstacle.rect.left < self.rect.right + HORIZONTAL_REACTION_DISTANCE
            )
            if is_horizontally_close:
                y_range = 300 * self.obstacle_avoidance_distance
                y_overlap = (
                    self.rect.top - y_range < obstacle.rect.bottom
                    and self.rect.bottom + y_range > obstacle.rect.top
                )

                if y_overlap:
                    self.obstacle_found_ahead = (
                        True  # Signal that an obstacle requires evasion
                    )
                    if self.rect.centery < obstacle.rect.centery:
                        accumulated_vertical_force_component -= (
                            VERTICAL_EVASION_MAGNITUDE
                        )
                    elif self.rect.centery > obstacle.rect.centery:
                        accumulated_vertical_force_component += (
                            VERTICAL_EVASION_MAGNITUDE
                        )

        if self.obstacle_found_ahead:
            # Apply the calculated purely vertical avoidance force.
            # The x-component of the avoidance force is zero for this strategy.
            self.apply_new_velocity(
                0,  # No horizontal steering from this specific avoidance logic
                accumulated_vertical_force_component,
                self.avoidance_strength
                * 10,  # Bird's overall avoidance strength attribute
            )

    def move_towards_food(self, food_group, all_birds_group):
        if not food_group:  # No food to move towards
            return

        closest_food = None
        min_dist_sq = float("inf")

        for food_item in food_group.sprites():
            if not hasattr(food_item, "rect"):
                continue  # Ensure food item has a rect

            dx = food_item.rect.centerx - self.x
            dy = food_item.rect.centery - self.y
            dist_sq = dx**2 + dy**2

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_food = food_item

        if closest_food:
            # Vector from bird to the closest food
            food_force_x = closest_food.rect.centerx - self.x
            food_force_y = closest_food.rect.centery - self.y

            self.apply_new_velocity(
                food_force_x, food_force_y, self.food_attraction_strength / 10
            )

            # --- EATING FOOD ---
            # You should also handle what happens when a bird reaches food.
            # This is typically a collision check.
            if pygame.sprite.collide_rect(self, closest_food):
                closest_food.kill()  # Remove food from all groups
                self.food_counter += 1
                # --- Reproduction Logic ---
                if self.food_counter >= REPRODUCTION_THRESHOLD:
                    self.food_counter = 0  # Reset counter for this bird

                    spawn_x = self.x + random.uniform(-15, 15)  # Spawn near parent
                    spawn_y = self.y + random.uniform(-15, 15)

                    # Ensure new bird spawns within screen bounds and not stuck in wall
                    spawn_x = max(
                        self.radius + 1,
                        min(self.scree_width - (self.radius + 1), spawn_x),
                    )
                    spawn_y = max(
                        self.radius + 1,
                        min(self.screen_height - (self.radius + 1), spawn_y),
                    )

                    new_offspring = Bird(
                        x=spawn_x,
                        y=spawn_y,
                        cohesion_strength=self.cohesion_strength,
                        alignment_strength=self.alignment_strength,
                        separation_strength=self.separation_strength,
                        avoidance_strength=self.avoidance_strength,
                        food_attraction_strength=self.food_attraction_strength,
                        obstacle_avoidance_distance=self.obstacle_avoidance_distance,
                    )
                    all_birds_group.add(new_offspring)

    def update(
        self, birds_group, obstacles, food_group
    ):  # Removed target_pos if not needed
        """Applies forces, updates rotation, and moves the bird."""
        current_center = self.rect.center

        # --- 1. Calculate and apply forces ---
        self.avoid_obstacles(obstacles)
        collided_obstacle = pygame.sprite.spritecollideany(self, obstacles)
        if collided_obstacle:
            Bird.collision_count += 1  # Increment score for fatal collision
            self.kill()  # Remove sprite from all groups
            return  # Bird is killed, no further processing needed for this instance

        if not self.obstacle_found_ahead:
            self.flock(self.get_closest_n_birds(birds_group))
            self.move_towards_food(food_group, birds_group)  # Apply force towards food

        # --- 2. Rotate Sprite based on final direction ---
        angle_rad = math.atan2(-self.speed_y, self.speed_x)
        angle_deg = math.degrees(angle_rad)

        self.image = pygame.transform.rotate(self.base_image, angle_deg)

        self.rect = self.image.get_rect(center=current_center)

        # --- 3. Move the bird ---
        self.move()

    def get_closest_n_birds(self, birds_group):
        neighbors_with_distances = []
        for other_bird in birds_group.sprites():  # Iterate through all birds
            if other_bird is self:
                continue
            dx = other_bird.x - self.x
            dy = other_bird.y - self.y
            dist_sq = dx**2 + dy**2
            neighbors_with_distances.append((dist_sq, other_bird))

        closest_neighbor_tuples = heapq.nsmallest(
            NUM_FLOCK_NEIGHBORS, neighbors_with_distances
        )
        closest_birds = [bird_tuple[1] for bird_tuple in closest_neighbor_tuples]
        return closest_birds
