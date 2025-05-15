# pygame_swarm_git/swarm_retro/Bird_class.py
import heapq
import math
import random
import pygame
import config_retro as cfg # Wichtig für den Zugriff auf cfg.KONSTANTEN
from config_retro import ( # Spezifische Imports, wenn direkt ohne cfg. Präfix verwendet
    BIRD_RADIUS, BIRD_SEPARATION_DISTANCE,
    BIRD_MUTATION_RATE, AVOIDANCE_GENE_MUTATION_RATE,
    WIDTH, HEIGHT, 
    BIRD_PREDICTION_HORIZON_MIN, BIRD_PREDICTION_HORIZON_MAX,
    BIRD_REACTION_STRENGTH_MIN, BIRD_REACTION_STRENGTH_MAX,
    BIRD_PREDICTION_AVOID_STRENGTH_FACTOR
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
        cohesion_strength=None,
        alignment_strength=None,
        separation_strength=None,
        global_speed_factor=None,
        slider_avoidance_strength=None,
        energy=None,
        prediction_horizon=None,
        reaction_strength=None
    ):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.cohesion_strength = cohesion_strength if cohesion_strength is not None else cfg.DEFAULT_COHESION
        self.alignment_strength = alignment_strength if alignment_strength is not None else cfg.DEFAULT_ALIGNMENT
        self.separation_strength = separation_strength if separation_strength is not None else cfg.DEFAULT_SEPARATION
        self.global_speed_factor = global_speed_factor if global_speed_factor is not None else cfg.DEFAULT_SPEED
        
        self.energy = energy if energy is not None else cfg.BIRD_INITIAL_ENERGY
        self.energy_threshold_reproduction = cfg.BIRD_ENERGY_THRESHOLD_REPRODUCTION # KORRIGIERT
        self.reproduction_cost = cfg.BIRD_REPRODUCTION_COST                         # KORRIGIERT
        
        self.slider_avoidance_strength = slider_avoidance_strength if slider_avoidance_strength is not None else cfg.DEFAULT_AVOIDANCE_SLIDER
        self.prediction_horizon = prediction_horizon if prediction_horizon is not None else cfg.BIRD_PREDICTION_HORIZON_DEFAULT
        self.reaction_strength = reaction_strength if reaction_strength is not None else cfg.BIRD_REACTION_STRENGTH_DEFAULT

        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        self.speed_x = math.cos(angle)
        self.speed_y = math.sin(angle)
        self.normalize_velocity()

        self.radius = BIRD_RADIUS
        self.color = (20, 20, 20)
        self.separation_distance = BIRD_SEPARATION_DISTANCE

        base_size = BIRD_RADIUS * 2.5
        surf_size = int(base_size * 1.5)
        center_offset = surf_size / 2
        tip = (center_offset + base_size * 0.6, center_offset)
        wing_top = (center_offset - base_size * 0.4, center_offset - base_size * 0.4)
        wing_bottom = (center_offset - base_size * 0.4, center_offset + base_size * 0.4)
        self.base_image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        pygame.draw.polygon(self.base_image, self.color, [tip, wing_top, wing_bottom])
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))
        self.mask = pygame.mask.from_surface(self.image)

        self.obstacle_found_ahead = False
        self.predicted_collision_imminent = False

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
        self.rect.center = (round(self.x), round(self.y))

    def flock(self, spatial_grid):
        closest_birds = spatial_grid.get_nearby_birds(self)
        if not closest_birds: return
        neighbors = [b for b in closest_birds if b is not self]
        if not neighbors: return
        neighbors = heapq.nsmallest(8, neighbors, key=lambda bird: (bird.x - self.x) ** 2 + (bird.y - self.y) ** 2)
        if not neighbors: return

        avg_vx = sum(bird.speed_x for bird in neighbors) / len(neighbors)
        avg_vy = sum(bird.speed_y for bird in neighbors) / len(neighbors)
        self.apply_force(avg_vx - self.speed_x, avg_vy - self.speed_y, self.alignment_strength)

        avg_x = sum(bird.x for bird in neighbors) / len(neighbors)
        avg_y = sum(bird.y for bird in neighbors) / len(neighbors)
        self.apply_force((avg_x - self.x) * 0.01, (avg_y - self.y) * 0.01, self.cohesion_strength)

        sep_fx, sep_fy = 0.0, 0.0
        for other in neighbors:
            dx, dy = self.x - other.x, self.y - other.y
            dist_sq = dx**2 + dy**2
            if 0 < dist_sq < self.separation_distance**2:
                inv_dist_sq = 1.0 / (dist_sq + 1e-5)
                sep_fx += dx * inv_dist_sq
                sep_fy += dy * inv_dist_sq
        self.apply_force(sep_fx, sep_fy, self.separation_strength)

    def apply_force(self, force_x, force_y, weight):
        self.speed_x += force_x * weight * 0.1
        self.speed_y += force_y * weight * 0.1

    def _check_future_collision(self, comet, horizon):
        bird_fut_x = self.x + self.speed_x * horizon
        bird_fut_y = self.y + self.speed_y * horizon
        comet_fut_x = comet.current_x + comet.speed_x * horizon
        comet_fut_y = comet.current_y + comet.speed_y * horizon
        comet_effective_radius = (comet.rect.width + comet.rect.height) / 4 
        collision_radius_sum_sq = (BIRD_RADIUS + comet_effective_radius)**2
        dist_sq_future = (bird_fut_x - comet_fut_x)**2 + (bird_fut_y - comet_fut_y)**2
        if dist_sq_future < collision_radius_sum_sq:
            return True, (comet_fut_x, comet_fut_y)
        return False, None

    def avoid_obstacles(self, obstacles_group):
        self.obstacle_found_ahead = False
        self.predicted_collision_imminent = False
        final_avoid_force_x = 0.0
        final_avoid_force_y = 0.0
        prediction_active_this_frame = False
        sorted_obstacles = list(obstacles_group)

        for comet in sorted_obstacles:
            if not hasattr(comet, 'current_x'): continue
            dist_sq_current = (self.x - comet.current_x)**2 + (self.y - comet.current_y)**2
            if dist_sq_current < (150)**2 and (abs(self.speed_x) > 0.1 or abs(self.speed_y) > 0.1) :
                collided_future, future_comet_pos = self._check_future_collision(comet, int(self.prediction_horizon))
                if collided_future:
                    self.predicted_collision_imminent = True
                    prediction_active_this_frame = True
                    dx_future = self.x - future_comet_pos[0] 
                    dy_future = self.y - future_comet_pos[1]
                    dist_future = math.sqrt(dx_future**2 + dy_future**2 + 1e-5)
                    strength = BIRD_PREDICTION_AVOID_STRENGTH_FACTOR * (1.0 / (dist_future + 1e-2)) * 50
                    final_avoid_force_x += (dx_future / dist_future) * strength
                    final_avoid_force_y += (dy_future / dist_future) * strength
                    break 
            if not prediction_active_this_frame:
                reactive_avoid_distance_sq = (80)**2
                if 0 < dist_sq_current < reactive_avoid_distance_sq:
                    dist_current = math.sqrt(dist_sq_current)
                    to_obstacle_x = comet.current_x - self.x
                    to_obstacle_y = comet.current_y - self.y
                    norm_to_obs_x = to_obstacle_x / dist_current
                    norm_to_obs_y = to_obstacle_y / dist_current
                    current_speed_mag = math.sqrt(self.speed_x**2 + self.speed_y**2 + 1e-5)
                    norm_vel_x = self.speed_x / current_speed_mag
                    norm_vel_y = self.speed_y / current_speed_mag
                    dot_product = norm_vel_x * norm_to_obs_x + norm_vel_y * norm_to_obs_y
                    if dot_product > COS_30_DEGREES:
                        self.obstacle_found_ahead = True
                        strength = (1.0 - (dist_current / math.sqrt(reactive_avoid_distance_sq))) * 1.0 
                        final_avoid_force_x -= norm_to_obs_x * strength
                        final_avoid_force_y -= norm_to_obs_y * strength
        
        if self.obstacle_found_ahead or self.predicted_collision_imminent:
            effective_strength_modifier = self.reaction_strength * self.slider_avoidance_strength
            self.apply_force(final_avoid_force_x, final_avoid_force_y, effective_strength_modifier)

        collided_obstacles_list = pygame.sprite.spritecollide(self, obstacles_group, False, pygame.sprite.collide_mask)
        if collided_obstacles_list:
            Bird.collision_count += 1
            self.kill()

    def seek_food(self, food_group):
        if not food_group or self.energy > self.energy_threshold_reproduction * 0.8: return
        closest_food, min_dist_sq = None, (150)**2
        for food_item in food_group:
            dist_sq = (self.x - food_item.rect.centerx)**2 + (self.y - food_item.rect.centery)**2
            if dist_sq < min_dist_sq: min_dist_sq, closest_food = dist_sq, food_item
        if closest_food:
            self.apply_force(closest_food.rect.centerx - self.x, closest_food.rect.centery - self.y, 0.05)

    def eat_food(self, food_group):
        for food_item in pygame.sprite.spritecollide(self, food_group, True, pygame.sprite.collide_rect):
            self.energy += food_item.energy_value

    def mutate_factors(self):
        rate = BIRD_MUTATION_RATE
        self.cohesion_strength = max(0.01, min(1.0, self.cohesion_strength + random.uniform(-rate, rate) * self.cohesion_strength))
        self.alignment_strength = max(0.01, min(1.0, self.alignment_strength + random.uniform(-rate, rate) * self.alignment_strength))
        self.separation_strength = max(0.01, min(1.0, self.separation_strength + random.uniform(-rate, rate) * self.separation_strength))
        avoid_rate = AVOIDANCE_GENE_MUTATION_RATE
        self.prediction_horizon += random.uniform(-avoid_rate, avoid_rate) * self.prediction_horizon
        self.prediction_horizon = max(BIRD_PREDICTION_HORIZON_MIN, min(BIRD_PREDICTION_HORIZON_MAX, int(self.prediction_horizon)))
        self.reaction_strength += random.uniform(-avoid_rate, avoid_rate) * self.reaction_strength
        self.reaction_strength = max(BIRD_REACTION_STRENGTH_MIN, min(BIRD_REACTION_STRENGTH_MAX, self.reaction_strength))

    def reproduce(self):
        if self.energy >= self.energy_threshold_reproduction: # Greift jetzt auf self.energy_threshold_reproduction zu
            self.energy -= self.reproduction_cost          # Greift jetzt auf self.reproduction_cost zu
            new_bird = Bird(
                self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5),
                self.screen_width, self.screen_height,
                self.cohesion_strength, self.alignment_strength,
                self.separation_strength,
                self.global_speed_factor,
                self.slider_avoidance_strength,
                energy=cfg.BIRD_INITIAL_ENERGY, # Neuer Vogel startet mit Initialenergie aus config
                prediction_horizon=self.prediction_horizon,
                reaction_strength=self.reaction_strength
            )
            new_bird.mutate_factors()
            return new_bird
        return None

    def update(self, spatial_grid, obstacles_group, food_group):
        if not self.alive(): return None
        current_center = self.rect.center

        self.avoid_obstacles(obstacles_group)
        if not self.alive(): return None

        if not self.obstacle_found_ahead and not self.predicted_collision_imminent:
            self.flock(spatial_grid)
            self.seek_food(food_group)

        self.eat_food(food_group)
        
        if self.energy < 0:
            self.kill(); return None

        current_speed_mag_sq = self.speed_x**2 + self.speed_y**2
        if current_speed_mag_sq > 1e-4:
            angle_rad = math.atan2(-self.speed_y, self.speed_x)
            angle_deg = math.degrees(angle_rad)
            self.image = pygame.transform.rotate(self.base_image, angle_deg)
            self.rect = self.image.get_rect(center=current_center)
            self.mask = pygame.mask.from_surface(self.image)
        
        self.move()

        if self.alive():
            return self.reproduce()
        return None