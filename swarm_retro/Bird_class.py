# pygame_swarm_git/swarm_retro/Bird_class.py
import heapq
import math
import random
import pygame
from config_retro import (
    BIRD_RADIUS, BIRD_SEPARATION_DISTANCE,
    BIRD_INITIAL_ENERGY, BIRD_ENERGY_THRESHOLD_REPRODUCTION,
    BIRD_REPRODUCTION_COST, BIRD_MUTATION_RATE,
    WIDTH, HEIGHT
)

COS_30_DEGREES = math.cos(math.radians(30))

class Bird(pygame.sprite.Sprite):
    collision_count = 0

    def __init__(
        self,
        x,
        y,
        screen_width,
        screen_height,
        cohesion_strength=0.10,
        alignment_strength=0.13,
        separation_strength=0.7,
        global_speed_factor=0.8,
        avoidance_strength=0.08,
        energy=None
    ):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

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
        self.normalize_velocity()

        self.radius = BIRD_RADIUS
        self.color = (20, 20, 20)
        self.separation_distance = BIRD_SEPARATION_DISTANCE

        self.energy = energy if energy is not None else BIRD_INITIAL_ENERGY
        self.energy_threshold_reproduction = BIRD_ENERGY_THRESHOLD_REPRODUCTION
        self.reproduction_cost = BIRD_REPRODUCTION_COST
        self.mutation_rate = BIRD_MUTATION_RATE

        base_size = self.radius * 2.5
        surf_size = int(base_size * 1.5)
        center_offset = surf_size / 2
        tip = (center_offset + base_size * 0.6, center_offset)
        wing_top = (center_offset - base_size * 0.4, center_offset - base_size * 0.4)
        wing_bottom = (center_offset - base_size * 0.4, center_offset + base_size * 0.4)
        self.base_image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        pygame.draw.polygon(self.base_image, self.color, [tip, wing_top, wing_bottom])
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image) # Erstelle Maske nach Image-Erstellung

        self.obstacle_found_ahead = False


    def normalize_velocity(self, max_speed=1.0):
        magnitude = math.sqrt(self.speed_x**2 + self.speed_y**2)
        if magnitude > 0:
            self.speed_x = (self.speed_x / magnitude) * max_speed
            self.speed_y = (self.speed_y / magnitude) * max_speed
        elif magnitude == 0 and max_speed > 0 :
            angle = random.uniform(0, 2 * math.pi)
            self.speed_x = math.cos(angle) * max_speed
            self.speed_y = math.sin(angle) * max_speed


    def move(self):
        current_max_speed = self.global_speed_factor
        self.normalize_velocity(max_speed=current_max_speed)

        self.x += self.speed_x
        self.y += self.speed_y

        if self.x < 0: self.x = self.screen_width
        if self.x > self.screen_width: self.x = 0
        if self.y < 0: self.y = self.screen_height
        if self.y > self.screen_height: self.y = 0
        
        self.rect.center = (self.x, self.y)


    def flock(self, spatial_grid):
        closest_birds = spatial_grid.get_nearby_birds(self)
        if not closest_birds: return
        
        neighbors = [b for b in closest_birds if b is not self]
        if not neighbors: return

        neighbors = heapq.nsmallest(8, neighbors, key=lambda bird: (bird.x - self.x) ** 2 + (bird.y - self.y) ** 2)
        if not neighbors: return

        avg_vx = sum(bird.speed_x for bird in neighbors) / len(neighbors)
        avg_vy = sum(bird.speed_y for bird in neighbors) / len(neighbors)
        alignment_force_x = avg_vx - self.speed_x
        alignment_force_y = avg_vy - self.speed_y
        self.apply_force(alignment_force_x, alignment_force_y, self.alignment_strength)

        avg_x = sum(bird.x for bird in neighbors) / len(neighbors)
        avg_y = sum(bird.y for bird in neighbors) / len(neighbors)
        cohesion_force_x = (avg_x - self.x) * 0.01
        cohesion_force_y = (avg_y - self.y) * 0.01
        self.apply_force(cohesion_force_x, cohesion_force_y, self.cohesion_strength)

        separation_force_x = 0
        separation_force_y = 0
        for other in neighbors:
            dx = self.x - other.x
            dy = self.y - other.y
            dist_sq = dx**2 + dy**2
            if 0 < dist_sq < self.separation_distance**2:
                inv_dist_sq = 1.0 / (dist_sq + 0.00001)
                separation_force_x += dx * inv_dist_sq
                separation_force_y += dy * inv_dist_sq
        self.apply_force(separation_force_x, separation_force_y, self.separation_strength)


    def apply_force(self, force_x, force_y, weight):
        self.speed_x += force_x * weight * 0.1
        self.speed_y += force_y * weight * 0.1


    def avoid_obstacles(self, obstacles_group):
        avoidance_force_x = 0
        avoidance_force_y = 0
        avoid_distance = 80
        lateral_steer_magnitude = 1.5
        self.obstacle_found_ahead = False

        for obstacle in obstacles_group:
            if not hasattr(obstacle, 'rect'): continue

            to_obstacle_x = obstacle.rect.centerx - self.x
            to_obstacle_y = obstacle.rect.centery - self.y
            dist_sq = to_obstacle_x**2 + to_obstacle_y**2

            if 0 < dist_sq < avoid_distance**2:
                dist = math.sqrt(dist_sq)
                norm_to_obs_x = to_obstacle_x / dist
                norm_to_obs_y = to_obstacle_y / dist

                current_speed_mag = math.sqrt(self.speed_x**2 + self.speed_y**2)
                if current_speed_mag < 0.001: continue

                norm_vel_x = self.speed_x / current_speed_mag
                norm_vel_y = self.speed_y / current_speed_mag
                
                dot_product = norm_vel_x * norm_to_obs_x + norm_vel_y * norm_to_obs_y

                if dot_product > COS_30_DEGREES:
                    self.obstacle_found_ahead = True
                    strength = (1.0 - (dist / avoid_distance)) * lateral_steer_magnitude
                    avoidance_force_x -= norm_to_obs_x * strength
                    avoidance_force_y -= norm_to_obs_y * strength
        
        if self.obstacle_found_ahead:
            self.apply_force(avoidance_force_x, avoidance_force_y, self.avoidance_strength)

        # Direkte Kollisionsprüfung für Tod (mit Maske für Pixelgenauigkeit)
        # Die Maske des Vogels muss bei Rotation aktualisiert werden (siehe update-Methode)
        collided_obstacles_list = pygame.sprite.spritecollide(self, obstacles_group, False, pygame.sprite.collide_mask)
        if collided_obstacles_list: # Gibt eine Liste der kollidierenden Hindernisse zurück
            # Bird.collision_count += len(collided_obstacles_list) # Zähle Todeskollisionen
            self.kill() # Vogel stirbt bei Kollision


    def seek_food(self, food_group):
        if not food_group or self.energy > self.energy_threshold_reproduction * 0.8:
            return

        closest_food = None
        min_dist_sq = (150)**2

        for food_item in food_group:
            dist_sq = (self.x - food_item.rect.centerx)**2 + (self.y - food_item.rect.centery)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_food = food_item
        
        if closest_food:
            dir_x = closest_food.rect.centerx - self.x
            dir_y = closest_food.rect.centery - self.y
            self.apply_force(dir_x, dir_y, 0.05)


    def eat_food(self, food_group):
        eaten_food_list = pygame.sprite.spritecollide(self, food_group, True)
        for food_item in eaten_food_list:
            self.energy += food_item.energy_value


    def mutate_factors(self):
        self.cohesion_strength += random.uniform(-self.mutation_rate, self.mutation_rate) * self.cohesion_strength
        self.alignment_strength += random.uniform(-self.mutation_rate, self.mutation_rate) * self.alignment_strength
        self.separation_strength += random.uniform(-self.mutation_rate, self.mutation_rate) * self.separation_strength
        self.cohesion_strength = max(0.01, min(1.0, self.cohesion_strength))
        self.alignment_strength = max(0.01, min(1.0, self.alignment_strength))
        self.separation_strength = max(0.01, min(1.0, self.separation_strength))

    def reproduce(self):
        if self.energy >= self.energy_threshold_reproduction:
            self.energy -= self.reproduction_cost
            new_bird = Bird(
                self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5),
                self.screen_width, self.screen_height,
                self.cohesion_strength, self.alignment_strength,
                self.separation_strength, self.global_speed_factor,
                self.avoidance_strength,
                energy=BIRD_INITIAL_ENERGY
            )
            new_bird.mutate_factors()
            return new_bird
        return None


    def update(self, spatial_grid, obstacles_group, food_group):
        if not self.alive():
            return None

        current_center = self.rect.center

        self.avoid_obstacles(obstacles_group) # Zuerst ausweichen/Kollision prüfen
        if not self.alive(): # Erneut prüfen, ob Vogel durch Kollision gestorben ist
            return None

        if not self.obstacle_found_ahead:
            self.flock(spatial_grid)
            self.seek_food(food_group)

        self.eat_food(food_group)
        # laufende Energie enziehen
        # self.energy -= 0.05
        if self.energy < 0:
            self.kill()
            return None

        if abs(self.speed_x) > 0.01 or abs(self.speed_y) > 0.01:
            angle_rad = math.atan2(-self.speed_y, self.speed_x)
            angle_deg = math.degrees(angle_rad)
            # Rotiere das Originalbild und weise es self.image zu
            self.image = pygame.transform.rotate(self.base_image, angle_deg)
            # Aktualisiere das rect mit dem neuen rotierten Bild und zentriere es neu
            self.rect = self.image.get_rect(center=current_center)
            # Aktualisiere die Maske nach der Rotation
            self.mask = pygame.mask.from_surface(self.image)


        self.move() # rect.center wird hier aktualisiert

        if self.alive():
            new_offspring = self.reproduce()
            return new_offspring
        return None