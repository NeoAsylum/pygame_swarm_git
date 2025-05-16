# pygame_swarm_git/swarm_retro/config_retro.py

# Screen dimensions
WIDTH = 1200
HEIGHT = 600
FPS = 60

# Bird properties
INITIAL_BIRDS = 50
BIRD_RADIUS = 3
BIRD_SEPARATION_DISTANCE = 40
BIRD_INITIAL_ENERGY = 100
BIRD_ENERGY_THRESHOLD_REPRODUCTION = 150
BIRD_REPRODUCTION_COST = 70
BIRD_MUTATION_RATE = 0.10 # Allgemeine Mutationsrate für Standardfaktoren (Cohesion, Alignment, Separation)

# Parameter für vorausschauendes Ausweichen & evolutionäre Anpassung
BIRD_PREDICTION_HORIZON_DEFAULT = 20 # Frames in die Zukunft für Vorhersage (Basiswert)
BIRD_PREDICTION_HORIZON_MIN = 5
BIRD_PREDICTION_HORIZON_MAX = 40
BIRD_PREDICTION_AVOID_STRENGTH_FACTOR = 1.5 # Multiplikator für Ausweichkraft bei vorhergesagter Kollision

# Genetisch beeinflusste Ausweichparameter
BIRD_REACTION_STRENGTH_DEFAULT = 0.7 # Basis-Reaktionsstärke (genetisch)
BIRD_REACTION_STRENGTH_MIN = 0.2
BIRD_REACTION_STRENGTH_MAX = 1.5
AVOIDANCE_GENE_MUTATION_RATE = 0.15 # Eigene Mutationsrate für Ausweich-Gene (prediction_horizon, reaction_strength)

BIRD_MAX_SPEED_FACTOR_SLIDER_EFFECT = 1.0 # Wird vom Speed-Slider als Basis-Maximalgeschwindigkeit genutzt

# Food properties
FOOD_SPAWN_RATE = 120 # Spawn food every X frames (e.g., every 2 seconds at 60 FPS)
MAX_FOOD_ITEMS = 30
FOOD_SIZE = 5
FOOD_ENERGY_VALUE = 25

# Comet (Moving Obstacle) properties
COMET_SIZE_W = 20
COMET_SIZE_H = 30
COMET_MIN_SPEED = 1
COMET_MAX_SPEED = 4 # Leicht erhöht für mehr Herausforderung
INITIAL_COMETS = 7    # Leicht erhöht
COMET_SPAWN_RATE = 150 # Etwas häufiger
MAX_COMETS_ON_SCREEN = 18 # Leicht erhöht

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)
UI_BUTTON_COLOR = (100, 180, 100)
UI_BUTTON_HOVER_COLOR = (130, 210, 130)
UI_BUTTON_TEXT_COLOR = (255, 255, 255)
UI_SLIDER_BG_COLOR = (200, 200, 200)
UI_SLIDER_BAR_COLOR = (100, 100, 220)
UI_SLIDER_HANDLE_COLOR = (80, 80, 80)
UI_TEXT_COLOR = (10, 10, 10)

# Slider defaults
DEFAULT_COHESION = 0.10
DEFAULT_ALIGNMENT = 0.14
DEFAULT_SEPARATION = 0.75
DEFAULT_SPEED = 0.8 # Beeinflusst global_speed_factor der Vögel
DEFAULT_AVOIDANCE_SLIDER = 0.5 # Globaler Modifikator für die genetische Reaktionsstärke der Vögel