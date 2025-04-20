import heapq
import math
import random
import pygame

white = (255, 255, 255)
blue = (0, 0, 255)
color = (20, 20, 20)
radius = 3
separation_distance = 50

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

        # Pygame sprite requirements
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image, self.color, (self.radius, self.radius), self.radius
        )
        self.rect = self.image.get_rect(center=(self.x, self.y))

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
        global collision_count  # Explicitly reference the global variable
        avoidance_force_x = 0
        avoidance_force_y = 0
        avoid_distance = 100  # Birds start avoiding obstacles from this distance

        for obstacle in obstacles:
            diff_x = self.x - (obstacle.x + obstacle.width / 2)
            diff_y = self.y - (obstacle.y + obstacle.height / 2)
            dist = math.sqrt(diff_x**2 + diff_y**2)
            if dist < avoid_distance:
                normalized_x = diff_x / dist
                normalized_y = diff_y / dist
                if self.rect.colliderect(obstacle.rect):  # Check collision
                    Bird.collision_count += 1  # Increment counter on collision
                force_magnitude = max(
                    0, 2.5 - (dist / avoid_distance)
                )  # Stronger force when closer
                avoidance_force_x += normalized_x * force_magnitude
                avoidance_force_y += normalized_y * force_magnitude

        # Apply the avoidance force in a smooth way
        self.apply_new_velocity(
            avoidance_force_x, avoidance_force_y, self.avoidance_strength
        )  # Slightly stronger steering

    def update(self, spatial_grid, obstacles):
        """Updates movement and flocking behavior when called by pygame.sprite.Group().update()"""
        self.move()
        self.flock(spatial_grid)
        self.avoid_obstacles(obstacles)  # Avoid obstacles before finalizing movement
