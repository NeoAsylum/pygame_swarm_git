import heapq
import math
import random
import pygame
from env import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DEFAULT_RADIUS,
    NUM_FLOCK_NEIGHBORS,
    REPRODUCTION_THRESHOLD,
    OBSTACLE_REACTION_DISTANCE_HORIZONTAL,
    OBSTACLE_VERTICAL_EVASION_MAGNITUDE,
    GLOBAL_SPEED_FACTOR,
)  # Import only necessary defaults
DEFAULT_OBSTACLE_AVOIDANCE_RADIUS = 100.0


class Bird(pygame.sprite.Sprite):
    """
    Represents a bird in the flocking simulation.

    Each bird has behaviors such as flocking (alignment, cohesion, separation),
    obstacle avoidance, and seeking food. Birds can also reproduce.
    The visual appearance of the bird is a simple animated sprite.
    """

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
        settings=None,  # Add settings parameter
    ):
        """
        Initializes a new Bird instance.

        Args:
            x (int): The initial x-coordinate of the bird.
            y (int): The initial y-coordinate of the bird.
            cohesion_strength (float, optional): Factor for cohesion behavior. Defaults to 0.1.
            alignment_strength (float, optional): Factor for alignment behavior. Defaults to 0.1.
            separation_strength (float, optional): Factor for separation behavior. Defaults to 0.1.
            avoidance_strength (float, optional): Factor for obstacle avoidance. Defaults to 0.1.
            food_attraction_strength (float, optional): Factor for food attraction. Defaults to 0.1.
            obstacle_avoidance_distance
            (float, optional): Factor for how far a bird
                                tries to stay from obstacles. Defaults to 0.1.
            settings (dict, optional): A dictionary of game settings that can influence
                                       bird behavior (e.g., GLOBAL_SPEED_FACTOR,
                                       NUM_FLOCK_NEIGHBORS, REPRODUCTION_THRESHOLD).
                                       Defaults to None, in which case global defaults from
                                       ENV.py are used.
        """
        super().__init__()
        self.settings = settings  # Store the settings
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
        self.food_attraction_strength = food_attraction_strength * random.uniform(
            0.9, 1.1
        )

        angle = random.uniform(0, 2 * math.pi)
        self.speed_x = math.cos(angle)
        self.speed_y = math.sin(angle)

        # --- Bird Visual Properties ---
        self.bird_width = DEFAULT_RADIUS * 5
        self.bird_height = DEFAULT_RADIUS * 3

        self.body_color = (170, 190, 220)  # Light bluish-grey
        self.wing_color = (140, 160, 190)  # Darker bluish-grey
        self.beak_color = (255, 180, 0)  # Bright orange/yellow
        self.eye_color = (0, 0, 0)

        self.radius = max(self.bird_width, self.bird_height) // 2
        # --- End of New Tiny Bird Visual Properties ---

        self.separation_distance = 50 * random.uniform(
            0.9, 1.1
        )  # User's original value
        self.food_counter = 0

        # --- Create the Base Image (Tiny Bird facing right) ---
        # For animation
        self.animation_frames = [
            self._create_tiny_bird_image(wing_offset=0),  # Wings normal
            self._create_tiny_bird_image(wing_offset=-2),  # Wings up
        ]
        self.current_frame_index = 0
        self.animation_timer = 0
        self.base_image = self.animation_frames[self.current_frame_index]

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def _create_tiny_bird_image(self, wing_offset=0):
        """
        Creates a Pygame Surface representing a small bird.

        The bird is drawn facing to the right, with a simple body, wing, beak, and eye.
        The wing position can be offset for animation.

        Args:
            wing_offset (int, optional): Vertical offset for the wing, used for flapping animation.
                                         Defaults to 0.

        Returns:
            pygame.Surface: A Surface object with the bird image.
        """
        image = pygame.Surface((self.bird_width, self.bird_height), pygame.SRCALPHA)
        body_rect = pygame.Rect(0, 1, self.bird_width - 3, self.bird_height - 2)
        pygame.draw.ellipse(image, self.body_color, body_rect)
        wing_width = int(self.bird_width * 0.4)
        wing_height = int(self.bird_height * 0.5)
        wing_x = body_rect.centerx - wing_width - 1
        wing_y = body_rect.centery - wing_height // 2 + wing_offset  # Apply offset
        pygame.draw.ellipse(
            image, self.wing_color, (wing_x, wing_y, wing_width, wing_height)
        )
        beak_tip_x = self.bird_width - 1
        beak_tip_y = self.bird_height // 2
        beak_base_x = self.bird_width - 4
        pygame.draw.polygon(
            image,
            self.beak_color,
            [
                (beak_tip_x, beak_tip_y),
                (beak_base_x, beak_tip_y - 2),
                (beak_base_x, beak_tip_y + 2),
            ],
        )
        eye_x = int(self.bird_width * 0.70)
        eye_y = int(self.bird_height * 0.35)
        pygame.draw.circle(image, self.eye_color, (eye_x, eye_y), 1)
        return image

    def move(self):
        """
        Updates the bird's position based on its current speed.
        Handles bouncing off the screen boundaries.
        The global speed factor from settings is applied.
        """
        # Use GLOBAL_SPEED_FACTOR from settings if available, otherwise from ENV.py
        current_global_speed_factor = GLOBAL_SPEED_FACTOR  # Default from ENV
        if self.settings and "GLOBAL_SPEED_FACTOR" in self.settings:
            current_global_speed_factor = self.settings["GLOBAL_SPEED_FACTOR"]

        self.x += self.speed_x * current_global_speed_factor
        self.y += self.speed_y * current_global_speed_factor

        if self.x <= self.radius or self.x >= self.scree_width - self.radius:
            self.speed_x *= -1
            # Clamp position after bounce to prevent getting stuck
            self.x = max(self.radius, min(self.scree_width - self.radius, self.x))
        if self.y <= self.radius or self.y >= self.screen_height - self.radius:
            self.speed_y *= -1
            # Clamp position after bounce
            self.y = max(self.radius, min(self.screen_height - self.radius, self.y))

    def flock(self, closest_birds):
        """
        Applies flocking behaviors (alignment, cohesion, separation) based on nearby birds.

        Args:
            closest_birds (list[Bird]): A list of the nearest
            neighboring birds to consider for flocking.
        """
        if (
            not closest_birds
        ):  # Added check to prevent division by zero if list is empty
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
            distance = (self.x - other.x) ** 2 + (
                self.y - other.y
            ) ** 2  # This is dist_sq
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
        """
        Applies a weighted force to the bird's velocity and normalizes the speed.

        Args:
            force_x (float): The x-component of the force to apply.
            force_y (float): The y-component of the force to apply.
            weight (float): The weighting factor for this force.
        """
        self.speed_x += force_x * weight * 0.027
        self.speed_y += force_y * weight * 0.027

        magnitude = math.hypot(self.speed_x, self.speed_y)
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude

    def avoid_obstacles(self, obstacles_group):
        """
        Calculates and applies forces to avoid obstacles using a predictive
        Closest Point of Approach (CPA) method. This helps birds maintain a
        minimum distance from obstacles.

        Args:
            obstacles_group (pygame.sprite.Group): A group of obstacle sprites.
        """
        accumulated_avoidance_force_x = 0.0
        accumulated_avoidance_force_y = 0.0

        # --- Constants for tuning avoidance behavior ---
        # Maximum number of frames to look into the future for CPA
        MAX_PREDICTION_HORIZON_FRAMES = 60  # How far to look ahead
        # Base magnitude for the repulsion force
        BASE_REPULSION_FORCE_MAGNITUDE = 200.0 # Overall strength of avoidance
        # Scalar for how much `self.obstacle_avoidance_distance` affects the safe distance buffer
        AVOIDANCE_DISTANCE_BUFFER_SCALAR = 150.0 # Translates trait to pixel buffer
        # Scalar for how much `self.obstacle_avoidance_distance` affects repulsion strength
        AVOIDANCE_STRENGTH_SENSITIVITY_SCALAR = 2.0 # How trait influences force
        # Epsilon for floating point comparisons to avoid division by zero
        EPSILON = 0.001

        # Get current global speed factor for accurate bird prediction
        current_global_speed_factor = GLOBAL_SPEED_FACTOR  # Default from ENV
        if self.settings and "GLOBAL_SPEED_FACTOR" in self.settings:
            current_global_speed_factor = self.settings["GLOBAL_SPEED_FACTOR"]

        # Bird's current velocity scaled by global speed factor
        bird_vx_gsf = self.speed_x * current_global_speed_factor
        bird_vy_gsf = self.speed_y * current_global_speed_factor

        for obstacle in obstacles_group:
            obs_hitbox = obstacle.hitbox  # Use the precise hitbox for calculations
            obs_speed_x = obstacle.speed_x  # Positive value, obstacle moves left

            # --- Broad phase filter: Is the obstacle roughly in a relevant zone? ---
            # Horizontal check: Consider obstacles within a wider range horizontally
            broad_horizontal_range = OBSTACLE_REACTION_DISTANCE_HORIZONTAL * 1.5
            interest_min_x = self.rect.left - broad_horizontal_range
            interest_max_x = self.rect.right + broad_horizontal_range

            # Vertical check: Consider obstacles within a reasonable vertical band
            vertical_interest_range = max(self.bird_height * 5, 100) + self.obstacle_avoidance_distance * 50
            interest_min_y = self.rect.centery - vertical_interest_range
            interest_max_y = self.rect.centery + vertical_interest_range

            obs_collides_with_interest_zone_x = obs_hitbox.right > interest_min_x and \
                                                obs_hitbox.left < interest_max_x
            obs_collides_with_interest_zone_y = obs_hitbox.bottom > interest_min_y and \
                                                obs_hitbox.top < interest_max_y
            
            bird_moving_right = bird_vx_gsf > EPSILON
            # obs_moving_left = obs_speed_x > EPSILON # Obstacle speed_x is always positive (moves left)

            is_relevant_horizontally = obs_collides_with_interest_zone_x or \
                                       (bird_moving_right and obs_hitbox.left < self.rect.right) or \
                                       (not bird_moving_right and obs_hitbox.right > self.rect.left)

            if not (is_relevant_horizontally and obs_collides_with_interest_zone_y):
                 continue # Skip obstacles outside the broad zone

            # --- CPA Calculation ---
            # Initial relative position vector (from obstacle center to bird center)
            R0_x = self.x - obs_hitbox.centerx
            R0_y = self.y - obs_hitbox.centery

            # Relative velocity vector (bird velocity - obstacle velocity)
            # Obstacle speed_x is positive, but it moves left (-x direction)
            Vrel_x = bird_vx_gsf - (-obs_speed_x)
            Vrel_y = bird_vy_gsf - 0 # Obstacle only moves horizontally

            Vrel_sq = Vrel_x**2 + Vrel_y**2

            t_cpa = float('inf')
            dist_cpa = float('inf')
            apply_force = False
            pred_bird_cpa_x = self.x # Initialize with current positions
            pred_bird_cpa_y = self.y
            pred_obs_cpa_x = obs_hitbox.centerx
            pred_obs_cpa_y = obs_hitbox.centery


            # Define the safe distance (sum of half-dimensions + buffer based on trait)
            bird_avg_dim = (self.bird_width + self.bird_height) * 0.25 # Using 0.25 for "half of average"
            obs_avg_dim = (obstacle.head_width + obstacle.head_height) * 0.25

            safe_distance = bird_avg_dim + obs_avg_dim + \
                            self.obstacle_avoidance_distance * AVOIDANCE_DISTANCE_BUFFER_SCALAR

            if Vrel_sq < EPSILON: # Relative velocity is near zero (moving parallel)
                t_cpa = 0 # Closest point is now
                dist_cpa = math.hypot(R0_x, R0_y)
                if dist_cpa < safe_distance:
                    apply_force = True
                # pred_bird_cpa_x,y and pred_obs_cpa_x,y remain as current positions
            else:
                # Time to closest point of approach: t = - (R0 . Vrel) / |Vrel|^2
                t_cpa = -(R0_x * Vrel_x + R0_y * Vrel_y) / Vrel_sq

                if 0 <= t_cpa <= MAX_PREDICTION_HORIZON_FRAMES:
                    # Predicted positions at t_cpa
                    pred_bird_cpa_x = self.x + bird_vx_gsf * t_cpa
                    pred_bird_cpa_y = self.y + bird_vy_gsf * t_cpa
                    pred_obs_cpa_x = obs_hitbox.centerx - obs_speed_x * t_cpa
                    pred_obs_cpa_y = obs_hitbox.centery # Obstacle only moves horizontally

                    # Distance at t_cpa
                    dist_cpa = math.hypot(pred_bird_cpa_x - pred_obs_cpa_x, pred_bird_cpa_y - pred_obs_cpa_y)

                    if dist_cpa < safe_distance:
                         apply_force = True

            if apply_force:
                # Evasion vector from predicted obstacle CPA to predicted bird CPA
                evasion_dx = pred_bird_cpa_x - pred_obs_cpa_x
                evasion_dy = pred_bird_cpa_y - pred_obs_cpa_y

                dist_at_pred_cpa = math.hypot(evasion_dx, evasion_dy)

                norm_evasion_dx = 0
                norm_evasion_dy = 0
                if dist_at_pred_cpa > EPSILON:
                    norm_evasion_dx = evasion_dx / dist_at_pred_cpa
                    norm_evasion_dy = evasion_dy / dist_at_pred_cpa
                else: # Overlap or same position at CPA, use current relative y for default push
                    if self.y < obs_hitbox.centery:
                        norm_evasion_dy = -1  # Push upwards
                    else:
                        norm_evasion_dy = 1   # Push downwards
                    # If still zero (e.g., y are equal), default to pushing downwards
                    if abs(norm_evasion_dx) < EPSILON and abs(norm_evasion_dy) < EPSILON:
                        norm_evasion_dy = 1


                # Magnitude of repulsion:
                # Stronger if CPA is sooner (time_factor closer to 1)
                # Stronger if CPA distance is much less than safe_distance (distance_factor closer to 1)
                effective_t_cpa = t_cpa if Vrel_sq >= EPSILON else 0.0 # Use 0 for parallel case urgency
                time_factor = max(0.0, 1.0 - (effective_t_cpa / MAX_PREDICTION_HORIZON_FRAMES))
                distance_factor = max(0.0, 1.0 - (dist_cpa / safe_distance))

                # Sensitivity multiplier based on bird's trait
                sensitivity_multiplier = (1.0 + self.obstacle_avoidance_distance * AVOIDANCE_STRENGTH_SENSITIVITY_SCALAR)

                repulsion_magnitude = BASE_REPULSION_FORCE_MAGNITUDE * time_factor * distance_factor * sensitivity_multiplier

                obstacle_force_x = norm_evasion_dx * repulsion_magnitude
                obstacle_force_y = norm_evasion_dy * repulsion_magnitude

                accumulated_avoidance_force_x += obstacle_force_x
                accumulated_avoidance_force_y += obstacle_force_y

        # After checking all obstacles, apply the accumulated avoidance force
        if accumulated_avoidance_force_x != 0 or accumulated_avoidance_force_y != 0:
            self.apply_new_velocity(accumulated_avoidance_force_x, accumulated_avoidance_force_y, self.avoidance_strength)


    def move_towards_food(self, food_group):
        """
        Moves the bird towards the closest food item and consumes it upon collision.

        Args:
            food_group (pygame.sprite.Group): A group of food sprites.
            all_birds_group (pygame.sprite.Group): The group containing all birds,
                                                   used for reproduction logic.
        """
        if not food_group:
            return

        closest_food = None
        min_dist_sq = float("inf")

        # Step 1: Find the single closest food item
        for food_item in food_group.sprites():
            if not hasattr(food_item, "rect"):  # Basic check
                continue
            dx = food_item.rect.centerx - self.x
            dy = food_item.rect.centery - self.y
            dist_sq = dx**2 + dy**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_food = food_item

        # Step 2: Act on the closest food (if one was found)
        # This entire block is now OUTSIDE the loop above.
        if closest_food:
            food_force_x = closest_food.rect.centerx - self.x
            food_force_y = closest_food.rect.centery - self.y

            magnitude = math.hypot(food_force_x, food_force_y)
            normalized_food_force_x = 0
            normalized_food_force_y = 0
            weight_for_food = 0  # Default weight if magnitude is 0

            if magnitude > 0:
                normalized_food_force_x = food_force_x / magnitude
                normalized_food_force_y = food_force_y / magnitude
                # Your weighting scheme: strength / original_distance
                weight_for_food = self.food_attraction_strength / magnitude

            self.apply_new_velocity(
                normalized_food_force_x,
                normalized_food_force_y,
                weight_for_food,  # Pass the calculated weight
            )

            # Check collision with the definitively closest food
            if pygame.sprite.collide_rect(self, closest_food):
                closest_food.kill()  # Remove the eaten food
                self.food_counter += 1

    def update(self, birds_group, obstacles, food_group):
        """
        Updates the bird's state for the current frame.

        This includes obstacle avoidance, flocking, moving towards food,
        handling reproduction, animation, and updating the bird's visual
        representation and position.

        Args:
            birds_group (pygame.sprite.Group): The group containing all bird sprites.
            obstacles (pygame.sprite.Group): The group containing all obstacle sprites.
            food_group (pygame.sprite.Group): The group containing all food sprites.
        """
        self.avoid_obstacles(obstacles)
        for obstacle in obstacles:
            if hasattr(obstacle, "hitbox"):
                if self.rect.colliderect(obstacle.hitbox):
                    self.kill()
                    return

        closest_birds_for_flocking = self.get_closest_n_birds(birds_group)
        if closest_birds_for_flocking:  # Only flock if neighbors are found
            self.flock(closest_birds_for_flocking)
        self.move_towards_food(food_group)  # Pass birds_group for reproduction

        # Animation
        self.animation_timer += 1
        if self.animation_timer > 5:  # Change frame every 5 game ticks
            self.animation_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(
                self.animation_frames
            )
            self.base_image = self.animation_frames[self.current_frame_index]

        if self.speed_x != 0 or self.speed_y != 0:
            angle_deg = math.degrees(math.atan2(-self.speed_y, self.speed_x))
            # Rotate the current base_image (which might be a different animation frame)
            self.image = pygame.transform.rotate(self.base_image, angle_deg)
        bird: Bird

        # Use REPRODUCTION_THRESHOLD from settings if available, otherwise from ENV.py
        current_reproduction_threshold = REPRODUCTION_THRESHOLD  # Default from ENV
        if self.settings and "REPRODUCTION_THRESHOLD" in self.settings:
            current_reproduction_threshold = self.settings["REPRODUCTION_THRESHOLD"]

        for bird in birds_group:
            if (
                bird is not self
                and pygame.sprite.collide_rect(self, bird)
                and self.food_counter >= current_reproduction_threshold
            ):
                self.food_counter = 0  # Reset counter for this parent bird
                bird.food_counter = 0
                new_offspring = Bird(
                    x=self.x,
                    y=self.y,
                    cohesion_strength=(self.cohesion_strength + bird.cohesion_strength)
                    / 2,
                    alignment_strength=(
                        self.alignment_strength + bird.alignment_strength
                    )
                    / 2,
                    separation_strength=(
                        self.separation_strength + bird.separation_strength
                    )
                    / 2,
                    avoidance_strength=(
                        self.avoidance_strength + bird.avoidance_strength
                    )
                    / 2,
                    food_attraction_strength=(
                        self.food_attraction_strength + bird.food_attraction_strength
                    )
                    / 2,
                    obstacle_avoidance_distance=(
                        self.obstacle_avoidance_distance
                        + bird.obstacle_avoidance_distance
                    )
                    / 2,
                    settings=self.settings,  # Pass settings to offspring
                )
                birds_group.add(new_offspring)

        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.move()
        self.rect.center = (
            int(self.x),
            int(self.y),
        )

    def get_closest_n_birds(self, birds_group):
        """
        Finds the N closest neighboring birds to this bird.

        The number of neighbors (N) is determined by NUM_FLOCK_NEIGHBORS,
        which can be overridden by game settings.

        Args:
            birds_group (pygame.sprite.Group): The group of all bird sprites.

        Returns:
            list[Bird]: A list containing the N closest birds.
        """
        # Use NUM_FLOCK_NEIGHBORS from settings if available, otherwise from ENV.py
        num_neighbors_to_consider = NUM_FLOCK_NEIGHBORS  # Default from ENV
        if self.settings and "NUM_FLOCK_NEIGHBORS" in self.settings:
            num_neighbors_to_consider = self.settings["NUM_FLOCK_NEIGHBORS"]

        neighbors_with_distances = []
        for other_bird in birds_group.sprites():
            if other_bird is self:
                continue
            dx = other_bird.x - self.x
            dy = other_bird.y - self.y
            dist_sq = dx**2 + dy**2
            neighbors_with_distances.append((dist_sq, id(other_bird), other_bird))

        closest_neighbor_tuples = heapq.nsmallest(
            num_neighbors_to_consider,
            neighbors_with_distances,
        )
        closest_birds = [bird_tuple[2] for bird_tuple in closest_neighbor_tuples]
        return closest_birds
