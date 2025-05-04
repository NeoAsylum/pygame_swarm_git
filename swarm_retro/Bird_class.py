import heapq
import math
import random
import pygame

white = (255, 255, 255)
blue = (0, 0, 255)
color = (20, 20, 20)
radius = 3
separation_distance = 50
COS_30_DEGREES = math.cos(math.radians(30)) # approx 0.866


class Bird(pygame.sprite.Sprite):
    collision_count = 0

    def __init__(
        self,
        x,
        y,
        width,
        height,
        cohesion_strength=0.10,
        alignment_strength=0.13,
        separation_strength=0.7,
        global_speed_factor=0.8,
        avoidance_strength=0.08,
    ):
        super().__init__()
        self.width = width  # Store screen width
        self.height = height  # Store screen height
        self.cohesion_strength = cohesion_strength
        self.alignment_strength = alignment_strength
        self.separation_strength = separation_strength
        self.global_speed_factor = global_speed_factor
        self.avoidance_strength = avoidance_strength
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        self.speed_x = math.cos(angle)
        self.speed_y = math.sin(angle)
        magnitude = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude

        self.radius = 3
        self.color = (20, 20, 20)
        self.separation_distance = 50

         # --- Create the Base Image (Triangle pointing right) ---
        # Size for the triangle base image
        base_size = self.radius * 2.5 # Make it slightly larger than diameter for better look
        # Points for a simple triangle pointing right (+X direction)
        # Centered roughly within the surface for better rotation pivot
        # Surface needs to be large enough to hold the rotated shape
        surf_size = int(base_size * 1.5) # Make surface larger than shape
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
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.obstacle_found_ahead = False

    def move(self):
        self.x += self.speed_x * self.global_speed_factor
        self.y += self.speed_y * self.global_speed_factor

        # Instant boundary reversal
        if self.x <= self.radius or self.x >= self.width - self.radius:
            self.speed_x *= -1
        if self.y <= self.radius or self.y >= self.height - self.radius:
            self.speed_y *= -1

        self.x = max(self.radius, min(self.width - self.radius, self.x))
        self.y = max(self.radius, min(self.height - self.radius, self.y))

        self.rect.center = (self.x, self.y)

    def flock(self, spatial_grid):
        closest_birds = spatial_grid.get_nearby_birds(self)
        if not closest_birds:
            return
        closest_birds = heapq.nsmallest(
            8,
            closest_birds,
            key=lambda bird: (bird.x - self.x) ** 2 + (bird.y - self.y) ** 2,
        )

        # Compute average movement
        avg_vx = sum(bird.speed_x for bird in closest_birds) / len(closest_birds)
        avg_vy = sum(bird.speed_y for bird in closest_birds) / len(closest_birds)
        alignment_force_x = avg_vx - self.speed_x
        alignment_force_y = avg_vy - self.speed_y
        self.apply_new_velocity(
            alignment_force_x, alignment_force_y, self.alignment_strength
        )

        avg_x = sum(bird.x for bird in closest_birds) / len(closest_birds)
        avg_y = sum(bird.y for bird in closest_birds) / len(closest_birds)
        cohesion_force_x = (avg_x - self.x) / 10
        cohesion_force_y = (avg_y - self.y) / 10
        self.apply_new_velocity(
            cohesion_force_x, cohesion_force_y, self.cohesion_strength / 2
        )

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
            separation_force_x, separation_force_y, self.separation_strength / 30
        )

    def apply_new_velocity(self, force_x, force_y, weight):
        self.speed_x += force_x * weight * 0.03
        self.speed_y += force_y * weight * 0.03

        magnitude = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if magnitude > 0:
            self.speed_x /= magnitude
            self.speed_y /= magnitude

    def avoid_obstacles(self, obstacles):
        avoidance_force_x = 0
        avoidance_force_y = 0
        # --- Parameters ---
        avoid_distance = 100  # Start checking distance
        # *** Strength of the sideways push when avoiding. TUNE THIS! ***
        lateral_steer_magnitude = 2.5 # Increased slightly, adjust as needed

        # Reset flag at the start of the check
        self.obstacle_found_ahead = False # Use the original flag name

        for obstacle in obstacles:
            if not hasattr(obstacle, 'rect'): continue
            obstacle_center_x = obstacle.rect.centerx
            obstacle_center_y = obstacle.rect.centery

            diff_x = self.x - obstacle_center_x
            diff_y = self.y - obstacle_center_y
            dist_sq = diff_x**2 + diff_y**2

            # --- Check 1: Close enough? ---
            if dist_sq < avoid_distance**2 and dist_sq > 1e-6:
                dist = math.sqrt(dist_sq)
                to_obstacle_x = -diff_x
                to_obstacle_y = -diff_y

                # --- Check 2: Within +/- 30 degree cone? ---
                dot_product = self.speed_x * to_obstacle_x + self.speed_y * to_obstacle_y
                if dot_product > dist * COS_30_DEGREES:
                    # Obstacle is relevant!
                    self.obstacle_found_ahead = True # Set the flag

                    # --- Check 3: Left or Right? ---
                    cross_product_z = self.speed_x * to_obstacle_y - self.speed_y * to_obstacle_x

                    # --- Calculate Lateral Steering Force ---
                    # Determine steering direction (perpendicular to velocity, away from obstacle)
                    steer_x = 0
                    steer_y = 0
                    if cross_product_z > 1e-6: # Obstacle is Left, steer Right (Clockwise 90deg rotation of velocity)
                        steer_x = self.speed_y
                        steer_y = -self.speed_x
                    elif cross_product_z < -1e-6: # Obstacle is Right, steer Left (Counter-Clockwise 90deg rotation)
                        steer_x = -self.speed_y
                        steer_y = self.speed_x

                    # Accumulate the LATERAL steering force if a direction was chosen
                    if abs(steer_x) > 1e-6 or abs(steer_y) > 1e-6:
                         avoidance_force_x += steer_x * lateral_steer_magnitude
                         avoidance_force_y += steer_y * lateral_steer_magnitude
        self.apply_new_velocity(
            avoidance_force_x, avoidance_force_y, self.avoidance_strength/2
        )
        # --- Collision Detection (Stats) ---
        if self.rect.colliderect(obstacle.rect):
            Bird.collision_count += 1

    def update(self, spatial_grid, obstacles): # Removed target_pos if not needed
        """Applies forces, updates rotation, and moves the bird."""
        # Store current center before forces change speed_x/y potentially
        current_center = self.rect.center

        # --- 1. Calculate and apply forces ---
        self.avoid_obstacles(obstacles)
        if not self.obstacle_found_ahead:
            self.flock(spatial_grid)

        # --- 2. Rotate Sprite based on final direction ---
        # Calculate angle from the velocity vector (speed_x, speed_y)
        # Use atan2 for accuracy; negate speed_y because Pygame's Y is inverted
        angle_rad = math.atan2(-self.speed_y, self.speed_x)
        angle_deg = math.degrees(angle_rad)

        # Rotate the *base* image to avoid quality degradation
        self.image = pygame.transform.rotate(self.base_image, angle_deg)

        # Get the new rect for the rotated image and *reset its center*
        # This ensures the sprite stays centered at its logical position (x, y)
        self.rect = self.image.get_rect(center=current_center)

        # --- 3. Move the bird ---
        # Move updates self.x, self.y and self.rect.center
        self.move()
        # Note: Since move updates self.rect.center AFTER rotation, the rotation
        # uses the center from the *start* of the update, and move sets the final one.
        # This is generally fine. Alternatively, rotate *after* move(), using self.x, self.y.