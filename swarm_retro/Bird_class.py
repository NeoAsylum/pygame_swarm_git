# pygame_swarm_git/swarm_retro/Bird_class.py
import heapq
import math
import random
import pygame
import config_retro as cfg

class Bird(pygame.sprite.Sprite):
    collision_count = 0
    reproduction_count = 0 # NEU: Globale Zählung aller Reproduktionen

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
        reaction_strength=None,
        hunger_drive_factor=None,
        low_energy_threshold_factor=None,
        passed_genes=None
    ):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height

        if passed_genes:
            self.cohesion_strength = passed_genes['cohesion']
            self.alignment_strength = passed_genes['alignment']
            self.separation_strength = passed_genes['separation']
            self.prediction_horizon = passed_genes['prediction_horizon']
            self.reaction_strength = passed_genes['reaction_strength']
            self.hunger_drive_factor = passed_genes.get('hunger_drive_factor', cfg.BIRD_HUNGER_DRIVE_FACTOR_DEFAULT)
            self.low_energy_threshold_factor = passed_genes.get('low_energy_threshold_factor', cfg.BIRD_LOW_ENERGY_THRESHOLD_FACTOR_DEFAULT)
        else:
            self.cohesion_strength = cohesion_strength if cohesion_strength is not None else cfg.DEFAULT_COHESION
            self.alignment_strength = alignment_strength if alignment_strength is not None else cfg.DEFAULT_ALIGNMENT
            self.separation_strength = separation_strength if separation_strength is not None else cfg.DEFAULT_SEPARATION
            self.prediction_horizon = prediction_horizon if prediction_horizon is not None else cfg.BIRD_PREDICTION_HORIZON_DEFAULT
            self.reaction_strength = reaction_strength if reaction_strength is not None else cfg.BIRD_REACTION_STRENGTH_DEFAULT
            self.hunger_drive_factor = hunger_drive_factor if hunger_drive_factor is not None else cfg.BIRD_HUNGER_DRIVE_FACTOR_DEFAULT
            self.low_energy_threshold_factor = low_energy_threshold_factor if low_energy_threshold_factor is not None else cfg.BIRD_LOW_ENERGY_THRESHOLD_FACTOR_DEFAULT

        self.global_speed_factor = global_speed_factor if global_speed_factor is not None else cfg.DEFAULT_SPEED

        if energy is None:
            self.energy = random.uniform(
                cfg.BIRD_INITIAL_ENERGY * cfg.BIRD_INITIAL_ENERGY_MIN_FACTOR,
                cfg.BIRD_INITIAL_ENERGY * cfg.BIRD_INITIAL_ENERGY_MAX_FACTOR
            )
        else:
            self.energy = energy

        self.energy_threshold_reproduction = cfg.BIRD_ENERGY_THRESHOLD_REPRODUCTION
        self.reproduction_cost = cfg.BIRD_REPRODUCTION_COST
        self.slider_avoidance_strength = slider_avoidance_strength if slider_avoidance_strength is not None else cfg.DEFAULT_AVOIDANCE_SLIDER

        self.actual_low_energy_threshold = self.low_energy_threshold_factor * self.energy_threshold_reproduction

        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, 2 * math.pi)
        self.speed_x = math.cos(angle)
        self.speed_y = math.sin(angle)
        self.normalize_velocity()

        self.radius = cfg.BIRD_RADIUS
        self.separation_distance_base = cfg.BIRD_SEPARATION_DISTANCE

        self.current_state = "NORMAL"
        self.color = cfg.BIRD_COLOR_NORMAL
        self._update_appearance()

        self.image = self.base_image
        self.rect = self.image.get_rect(center=(round(self.x), round(self.y)))
        self.mask = pygame.mask.from_surface(self.image)

        self.obstacle_found_ahead = False
        self.predicted_collision_imminent = False

    def _get_polygon_points(self, surf_size):
        base_size = cfg.BIRD_RADIUS * 2.5
        center_offset = surf_size / 2
        tip = (center_offset + base_size * 0.6, center_offset)
        wing_top = (center_offset - base_size * 0.4, center_offset - base_size * 0.4)
        wing_bottom = (center_offset - base_size * 0.4, center_offset + base_size * 0.4)
        return [tip, wing_top, wing_bottom]

    def _update_appearance(self):
        surf_size = int(cfg.BIRD_RADIUS * 2.5 * 1.5)
        self.base_image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        pygame.draw.polygon(self.base_image, self.color, self._get_polygon_points(surf_size))

    def _update_state_and_color(self):
        initial_color = self.color
        determined_color = self.color

        if self.energy < self.actual_low_energy_threshold:
            self.current_state = "LOW_ENERGY"
            determined_color = cfg.BIRD_COLOR_LOW_ENERGY
        elif self.predicted_collision_imminent or self.obstacle_found_ahead:
            self.current_state = "AVOIDING"
            determined_color = cfg.BIRD_COLOR_AVOIDING
        else:
            if self.current_state == "SEEKING_FOOD":
                determined_color = cfg.BIRD_COLOR_SEEKING_FOOD
            elif self.current_state == "REPRODUCING":
                determined_color = cfg.BIRD_COLOR_REPRODUCING
            elif self.current_state == "NORMAL":
                determined_color = cfg.BIRD_COLOR_NORMAL
            else:
                self.current_state = "NORMAL"
                determined_color = cfg.BIRD_COLOR_NORMAL
        
        if determined_color != initial_color:
            self.color = determined_color
            self._update_appearance()

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
        self.energy -= cfg.BIRD_ENERGY_COST_PER_TICK

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
        current_separation_distance = self.separation_distance_base * (1.0 + (self.separation_strength - cfg.DEFAULT_SEPARATION))
        for other in neighbors:
            dx, dy = self.x - other.x, self.y - other.y
            dist_sq = dx**2 + dy**2
            if 0 < dist_sq < current_separation_distance**2:
                inv_dist_sq = 1.0 / (dist_sq + 1e-5)
                sep_fx += dx * inv_dist_sq
                sep_fy += dy * inv_dist_sq
        self.apply_force(sep_fx, sep_fy, self.separation_strength)

    def apply_force(self, force_x, force_y, weight):
        self.speed_x += force_x * weight * 0.1
        self.speed_y += force_y * weight * 0.1

    def _check_future_collision(self, comet, horizon_frames):
        bird_fut_x = self.x + self.speed_x * horizon_frames
        bird_fut_y = self.y + self.speed_y * horizon_frames
        comet_fut_x = comet.current_x + comet.speed_x * horizon_frames
        comet_fut_y = comet.current_y + comet.speed_y * horizon_frames
        comet_effective_radius = (comet.rect.width + comet.rect.height) / 4
        dist_sq_future = (bird_fut_x - comet_fut_x)**2 + (bird_fut_y - comet_fut_y)**2
        collision_radius_sum_sq = (cfg.BIRD_RADIUS + comet_effective_radius)**2
        if dist_sq_future < collision_radius_sum_sq:
            return True, (comet_fut_x, comet_fut_y)
        return False, None

    def avoid_obstacles(self, obstacles_group):
        self.obstacle_found_ahead = False
        self.predicted_collision_imminent = False
        final_avoid_force_x = 0.0
        final_avoid_force_y = 0.0
        prediction_active_this_frame = False
        for comet in obstacles_group:
            if not hasattr(comet, 'current_x'): continue
            dist_sq_current = (self.x - comet.current_x)**2 + (self.y - comet.current_y)**2
            if dist_sq_current < cfg.PREDICTIVE_AVOIDANCE_CHECK_RADIUS_SQ and \
               (abs(self.speed_x) > 0.1 or abs(self.speed_y) > 0.1) :
                collided_future, future_comet_pos = self._check_future_collision(comet, int(self.prediction_horizon))
                if collided_future:
                    self.predicted_collision_imminent = True
                    prediction_active_this_frame = True
                    dx_future_threat = self.x - future_comet_pos[0]
                    dy_future_threat = self.y - future_comet_pos[1]
                    dist_future_threat = math.sqrt(dx_future_threat**2 + dy_future_threat**2 + 1e-5)
                    strength_factor = cfg.BIRD_PREDICTION_AVOID_STRENGTH_FACTOR
                    strength = strength_factor * (1.0 / (dist_future_threat + 1e-2)) * 50
                    final_avoid_force_x += (dx_future_threat / dist_future_threat) * strength
                    final_avoid_force_y += (dy_future_threat / dist_future_threat) * strength
                    self.energy -= cfg.BIRD_ENERGY_COST_AVOIDANCE_MANEUVER
                    break
            if not prediction_active_this_frame:
                if 0 < dist_sq_current < cfg.REACTIVE_AVOIDANCE_RADIUS_SQ:
                    dist_current = math.sqrt(dist_sq_current)
                    to_obstacle_x = comet.current_x - self.x
                    to_obstacle_y = comet.current_y - self.y
                    norm_to_obs_x = to_obstacle_x / dist_current
                    norm_to_obs_y = to_obstacle_y / dist_current
                    current_speed_mag = math.sqrt(self.speed_x**2 + self.speed_y**2 + 1e-5)
                    norm_vel_x = self.speed_x / current_speed_mag
                    norm_vel_y = self.speed_y / current_speed_mag
                    dot_product = norm_vel_x * norm_to_obs_x + norm_vel_y * norm_to_obs_y
                    if dot_product > cfg.REACTIVE_AVOIDANCE_FOV_COS:
                        self.obstacle_found_ahead = True
                        strength = (1.0 - (dist_current / math.sqrt(cfg.REACTIVE_AVOIDANCE_RADIUS_SQ))) * 1.0
                        final_avoid_force_x -= norm_to_obs_x * strength
                        final_avoid_force_y -= norm_to_obs_y * strength
                        self.energy -= cfg.BIRD_ENERGY_COST_AVOIDANCE_MANEUVER
        if self.obstacle_found_ahead or self.predicted_collision_imminent:
            effective_strength_modifier = self.reaction_strength * self.slider_avoidance_strength
            self.apply_force(final_avoid_force_x, final_avoid_force_y, effective_strength_modifier)
        collided_obstacles_list = pygame.sprite.spritecollide(self, obstacles_group, False, pygame.sprite.collide_mask)
        if collided_obstacles_list:
            Bird.collision_count += 1
            self.kill()

    def seek_food(self, food_group):
        food_seeking_threshold = self.energy_threshold_reproduction * self.hunger_drive_factor
        if not food_group or self.energy > food_seeking_threshold:
            if self.current_state == "SEEKING_FOOD":
                self.current_state = "NORMAL"
            return

        self.current_state = "SEEKING_FOOD"
        closest_food, min_dist_sq = None, float('inf')
        food_scan_radius_sq = 200**2
        for food_item in food_group:
            dist_sq = (self.x - food_item.rect.centerx)**2 + (self.y - food_item.rect.centery)**2
            if dist_sq < min_dist_sq and dist_sq < food_scan_radius_sq:
                min_dist_sq = dist_sq
                closest_food = food_item
        if closest_food:
            self.apply_force(closest_food.rect.centerx - self.x,
                             closest_food.rect.centery - self.y,
                             0.05)

    def eat_food(self, food_group):
        eaten_food_list = pygame.sprite.spritecollide(self, food_group, True, pygame.sprite.collide_rect)
        for food_item in eaten_food_list:
            self.energy += food_item.energy_value

    def mutate_factors(self):
        rate = cfg.BIRD_MUTATION_RATE
        avoid_rate = cfg.AVOIDANCE_GENE_MUTATION_RATE
        behavioral_rate = cfg.BIRD_BEHAVIORAL_GENE_MUTATION_RATE

        self.cohesion_strength = max(0.01, min(1.0, self.cohesion_strength + random.uniform(-rate, rate) * self.cohesion_strength))
        self.alignment_strength = max(0.01, min(1.0, self.alignment_strength + random.uniform(-rate, rate) * self.alignment_strength))
        self.separation_strength = max(0.01, min(1.0, self.separation_strength + random.uniform(-rate, rate) * self.separation_strength))
        self.prediction_horizon += random.uniform(-avoid_rate, avoid_rate) * self.prediction_horizon
        self.prediction_horizon = max(cfg.BIRD_PREDICTION_HORIZON_MIN, min(cfg.BIRD_PREDICTION_HORIZON_MAX, int(self.prediction_horizon)))
        self.reaction_strength += random.uniform(-avoid_rate, avoid_rate) * self.reaction_strength
        self.reaction_strength = max(cfg.BIRD_REACTION_STRENGTH_MIN, min(cfg.BIRD_REACTION_STRENGTH_MAX, self.reaction_strength))

        self.hunger_drive_factor += random.uniform(-behavioral_rate, behavioral_rate) * self.hunger_drive_factor
        self.hunger_drive_factor = max(cfg.BIRD_HUNGER_DRIVE_FACTOR_MIN, min(cfg.BIRD_HUNGER_DRIVE_FACTOR_MAX, self.hunger_drive_factor))
        self.low_energy_threshold_factor += random.uniform(-behavioral_rate, behavioral_rate) * self.low_energy_threshold_factor
        self.low_energy_threshold_factor = max(cfg.BIRD_LOW_ENERGY_THRESHOLD_FACTOR_MIN, min(cfg.BIRD_LOW_ENERGY_THRESHOLD_FACTOR_MAX, self.low_energy_threshold_factor))
        self.actual_low_energy_threshold = self.low_energy_threshold_factor * self.energy_threshold_reproduction

    def reproduce(self, spatial_grid):
        if self.energy >= self.energy_threshold_reproduction:
            self.energy -= self.reproduction_cost
            self.current_state = "REPRODUCING"

            partner_genes = None
            potential_mates = [
                p for p in spatial_grid.get_nearby_birds(self)
                if p is not self and p.energy >= p.energy_threshold_reproduction and
                math.hypot(self.x - p.x, self.y - p.y) < cfg.BIRD_MATING_RADIUS
            ]
            if potential_mates:
                partner = random.choice(potential_mates)
                partner_genes = {
                    'cohesion': partner.cohesion_strength,
                    'alignment': partner.alignment_strength,
                    'separation': partner.separation_strength,
                    'prediction_horizon': partner.prediction_horizon,
                    'reaction_strength': partner.reaction_strength,
                    'hunger_drive_factor': partner.hunger_drive_factor,
                    'low_energy_threshold_factor': partner.low_energy_threshold_factor,
                }

            child_genes = {}
            parent1_genes = {
                'cohesion': self.cohesion_strength, 'alignment': self.alignment_strength,
                'separation': self.separation_strength, 'prediction_horizon': self.prediction_horizon,
                'reaction_strength': self.reaction_strength,
                'hunger_drive_factor': self.hunger_drive_factor,
                'low_energy_threshold_factor': self.low_energy_threshold_factor,
            }

            for gene_name in parent1_genes.keys():
                if partner_genes and random.random() < cfg.BIRD_CROSSOVER_RATE:
                    child_genes[gene_name] = (parent1_genes[gene_name] + partner_genes[gene_name]) / 2.0
                else:
                    child_genes[gene_name] = parent1_genes[gene_name]
            
            new_bird = Bird(
                self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5),
                self.screen_width, self.screen_height,
                passed_genes=child_genes,
                global_speed_factor=self.global_speed_factor,
                slider_avoidance_strength=self.slider_avoidance_strength,
                energy=None
            )
            new_bird.mutate_factors()
            Bird.reproduction_count += 1 # NEU: Reproduktionszähler erhöhen
            self.current_state = "NORMAL"
            return new_bird

        return None # Zustand wird in _update_state_and_color() oder durch andere Aktionen ggf. angepasst

    def update(self, spatial_grid, obstacles_group, food_group):
        if not self.alive(): return None
        if self.energy < 0:
            self.kill()
            return None

        self.avoid_obstacles(obstacles_group)
        if not self.alive(): return None

        if not self.obstacle_found_ahead and not self.predicted_collision_imminent:
            self.flock(spatial_grid)
            self.seek_food(food_group)

        self.eat_food(food_group)
        
        offspring = None
        if self.alive():
            offspring = self.reproduce(spatial_grid)

        self._update_state_and_color()
        
        self.move()

        current_speed_mag_sq = self.speed_x**2 + self.speed_y**2
        if current_speed_mag_sq > 1e-4:
            angle_rad = math.atan2(-self.speed_y, self.speed_x)
            angle_deg = math.degrees(angle_rad)
            self.image = pygame.transform.rotate(self.base_image, angle_deg)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.mask = pygame.mask.from_surface(self.image)
        else:
             self.image = self.base_image
             self.rect = self.image.get_rect(center=self.rect.center)
             self.mask = pygame.mask.from_surface(self.image)
        
        return offspring