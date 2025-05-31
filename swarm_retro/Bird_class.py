import heapq
import math
import random
import pygame
from env import * # Assuming this imports SCREEN_WIDTH, SCREEN_HEIGHT, DEFAULT_RADIUS (if still used), GLOBAL_SPEED_FACTOR, etc.

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
        self.scree_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
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
        magnitude = math.hypot(self.speed_x, self.speed_y) # Using math.hypot
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude

        # --- New Tiny Bird Visual Properties ---
        self.bird_width = 15
        self.bird_height = 10

        self.body_color = (255, 230, 150)
        self.wing_color = (240, 210, 130)
        self.beak_color = (255, 165, 0)
        self.eye_color = (0, 0, 0)
        
        # Update self.radius based on new bird dimensions for boundary checks.
        # This replaces the old self.radius = DEFAULT_RADIUS
        self.radius = max(self.bird_width, self.bird_height) // 2
        # self.color = (20, 20, 20) # No longer used for the main bird image

        # --- End of New Tiny Bird Visual Properties ---

        self.separation_distance = 50 * random.uniform(0.9, 1.1) # User's original value
        self.food_counter = 0
        self.food_attraction_strength = food_attraction_strength * random.uniform(
            0.9, 1.1
        )

        # --- Create the Base Image (Tiny Bird facing right) ---
        self.base_image = self._create_tiny_bird_image()

        # Pygame sprite requirements
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.obstacle_found_ahead = False

    def _create_tiny_bird_image(self):
        """Creates a small, bird-like image facing right."""
        image = pygame.Surface((self.bird_width, self.bird_height), pygame.SRCALPHA)
        body_rect = pygame.Rect(0, 1, self.bird_width - 3, self.bird_height - 2)
        pygame.draw.ellipse(image, self.body_color, body_rect)
        wing_width = int(self.bird_width * 0.4)
        wing_height = int(self.bird_height * 0.5)
        wing_x = body_rect.centerx - wing_width - 1
        wing_y = body_rect.centery - wing_height // 2
        pygame.draw.ellipse(image, self.wing_color, (wing_x, wing_y, wing_width, wing_height))
        beak_tip_x = self.bird_width - 1
        beak_tip_y = self.bird_height // 2
        beak_base_x = self.bird_width - 4
        pygame.draw.polygon(image, self.beak_color, [
            (beak_tip_x, beak_tip_y),
            (beak_base_x, beak_tip_y - 2),
            (beak_base_x, beak_tip_y + 2)
        ])
        eye_x = int(self.bird_width * 0.70)
        eye_y = int(self.bird_height * 0.35)
        pygame.draw.circle(image, self.eye_color, (eye_x, eye_y), 1)
        return image

    def move(self):
        self.x += self.speed_x * GLOBAL_SPEED_FACTOR
        self.y += self.speed_y * GLOBAL_SPEED_FACTOR

        if self.x <= self.radius or self.x >= self.scree_width - self.radius:
            self.speed_x *= -1
            # Clamp position after bounce to prevent getting stuck
            self.x = max(self.radius, min(self.scree_width - self.radius, self.x))
        if self.y <= self.radius or self.y >= self.screen_height - self.radius:
            self.speed_y *= -1
            # Clamp position after bounce
            self.y = max(self.radius, min(self.screen_height - self.radius, self.y))
        
        # self.rect.center = (self.x, self.y) # Updated in update() after rotation

    def flock(self, closest_birds):
        # closest_birds # User's original had this line, likely a no-op or for debugging
        if not closest_birds: # Added check to prevent division by zero if list is empty
            return

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
        cohesion_force_x = (avg_x - self.x) / 10 # User's original / 10
        cohesion_force_y = (avg_y - self.y) / 10 # User's original / 10
        self.apply_new_velocity(
            cohesion_force_x, cohesion_force_y, self.cohesion_strength
        )

        # Separation
        separation_force_x = 0
        separation_force_y = 0
        epsilon = 0.00001 # User's original epsilon
        for other in closest_birds:
            distance = (self.x - other.x) ** 2 + (self.y - other.y) ** 2 # This is dist_sq
            # User's original comparison: distance < self.separation_distance
            # Assuming self.separation_distance (~50) is a threshold for squared distance
            if distance < self.separation_distance:
                diff_x = self.x - other.x
                diff_y = self.y - other.y
                force = 300 / (distance + epsilon) # User's original force calculation
                separation_force_x += diff_x * force
                separation_force_y += diff_y * force
        self.apply_new_velocity(
            separation_force_x, separation_force_y, self.separation_strength / 15 # User's original / 15
        )

    def apply_new_velocity(self, force_x, force_y, weight):
        self.speed_x += force_x * weight * 0.027 # User's original 0.027
        self.speed_y += force_y * weight * 0.027 # User's original 0.027

        magnitude = math.hypot(self.speed_x, self.speed_y) # Using math.hypot
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude
        # My addition for magnitude == 0 case (keeping for robustness, does not change original values if speed > 0)
        elif magnitude == 0 and (force_x != 0 or force_y != 0):
            force_mag = math.hypot(force_x, force_y)
            if force_mag > 0:
                self.speed_x = (force_x / force_mag)
                self.speed_y = (force_y / force_mag)


    def avoid_obstacles(self, obstacles_group):
        # User's original constants defined inside the method
        HORIZONTAL_REACTION_DISTANCE = 200
        VERTICAL_EVASION_MAGNITUDE = 1.5 # This was used by user

        accumulated_vertical_force_component = 0
        self.obstacle_found_ahead = False
        
        for obstacle in obstacles_group:
            # Using obstacle.rect as per user's original context for avoidance logic.
            # Fatal collision check in update() method uses hitbox.
            obstacle_check_rect = obstacle.rect

            is_horizontally_close = (
                obstacle_check_rect.right > self.rect.left
                and obstacle_check_rect.left < self.rect.right + HORIZONTAL_REACTION_DISTANCE
            )
            if is_horizontally_close:
                # User's original y_range calculation
                y_range = 300 * self.obstacle_avoidance_distance
                y_overlap = (
                    self.rect.top - y_range < obstacle_check_rect.bottom
                    and self.rect.bottom + y_range > obstacle_check_rect.top
                )

                if y_overlap:
                    self.obstacle_found_ahead = True
                    if self.rect.centery < obstacle_check_rect.centery:
                        accumulated_vertical_force_component -= VERTICAL_EVASION_MAGNITUDE
                    elif self.rect.centery > obstacle_check_rect.centery:
                        accumulated_vertical_force_component += VERTICAL_EVASION_MAGNITUDE
                    # If centery is same, no vertical force based on this logic
                    break # User's original structure might imply breaking after first relevant obstacle for avoidance steering


        if self.obstacle_found_ahead:
            self.apply_new_velocity(
                0,
                accumulated_vertical_force_component,
                self.avoidance_strength * 10  # User's original * 10
            )

    def move_towards_food(self, food_group, all_birds_group):
        if not food_group:
            return

        closest_food = None
        min_dist_sq = float("inf")

        for food_item in food_group.sprites():
            if not hasattr(food_item, "rect"):
                continue

            dx = food_item.rect.centerx - self.x
            dy = food_item.rect.centery - self.y
            dist_sq = dx**2 + dy**2

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_food = food_item

        if closest_food:
            food_force_x = closest_food.rect.centerx - self.x
            food_force_y = closest_food.rect.centery - self.y

            self.apply_new_velocity(
                food_force_x, food_force_y, self.food_attraction_strength / 10 # User's original / 10
            )

            if pygame.sprite.collide_rect(self, closest_food):
                closest_food.kill()
                self.food_counter += 1
                if self.food_counter >= REPRODUCTION_THRESHOLD: # Assuming REPRODUCTION_THRESHOLD is from env
                    self.food_counter = 0
                    spawn_x = self.x + random.uniform(-15, 15)
                    spawn_y = self.y + random.uniform(-15, 15)
                    spawn_x = max(self.radius + 1, min(self.scree_width - (self.radius + 1), spawn_x))
                    spawn_y = max(self.radius + 1, min(self.screen_height - (self.radius + 1), spawn_y))
                    new_offspring = Bird(
                        x=spawn_x, y=spawn_y,
                        cohesion_strength=self.cohesion_strength,
                        alignment_strength=self.alignment_strength,
                        separation_strength=self.separation_strength,
                        avoidance_strength=self.avoidance_strength,
                        food_attraction_strength=self.food_attraction_strength,
                        obstacle_avoidance_distance=self.obstacle_avoidance_distance,
                    )
                    all_birds_group.add(new_offspring)


    def update(self, birds_group, obstacles, food_group):
        current_center = (self.x, self.y) # Use precise float coords for center

        self.avoid_obstacles(obstacles)
        
        collided_with_head = False
        for obstacle in obstacles:
            if hasattr(obstacle, "hitbox"):
                if self.rect.colliderect(obstacle.hitbox):
                    collided_with_head = True
                    break
            else:
                if self.rect.colliderect(obstacle.rect):
                    collided_with_head = True
                    break
        
        if collided_with_head:
            Bird.collision_count += 1
            self.kill()
            return

        if not self.obstacle_found_ahead:
            closest_birds_for_flocking = self.get_closest_n_birds(birds_group)
            if closest_birds_for_flocking: # Only flock if neighbors are found
                 self.flock(closest_birds_for_flocking)
            self.move_towards_food(food_group, birds_group) # Pass birds_group for reproduction

        if self.speed_x != 0 or self.speed_y != 0:
            angle_rad = math.atan2(-self.speed_y, self.speed_x)
            angle_deg = math.degrees(angle_rad)
            self.image = pygame.transform.rotate(self.base_image, angle_deg)
        # else: self.image remains unchanged if speed is zero

        self.rect = self.image.get_rect(center=current_center)
        self.move()
        self.rect.center = (int(self.x), int(self.y)) # Update rect center after move, ensuring int for Pygame


    def get_closest_n_birds(self, birds_group):
        neighbors_with_distances = []
        for other_bird in birds_group.sprites():
            if other_bird is self:
                continue
            dx = other_bird.x - self.x
            dy = other_bird.y - self.y
            dist_sq = dx**2 + dy**2
            neighbors_with_distances.append((dist_sq, other_bird))
        
        closest_neighbor_tuples = heapq.nsmallest(
            NUM_FLOCK_NEIGHBORS, neighbors_with_distances # Assuming NUM_FLOCK_NEIGHBORS from env
        )
        closest_birds = [bird_tuple[1] for bird_tuple in closest_neighbor_tuples]
        return closest_birds