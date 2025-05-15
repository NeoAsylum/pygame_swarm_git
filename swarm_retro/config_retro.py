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
BIRD_ENERGY_THRESHOLD_REPRODUCTION = 150 # Energie benötigt für Reproduktion
BIRD_REPRODUCTION_COST = 70             # Energieverlust bei Reproduktion
BIRD_MUTATION_RATE = 0.1
BIRD_MAX_SPEED_FACTOR_SLIDER_EFFECT = 1.0

# Food properties
FOOD_SPAWN_RATE = 120 # Spawn food every X frames (e.g., every 2 seconds at 60 FPS)
MAX_FOOD_ITEMS = 30
FOOD_SIZE = 5
FOOD_ENERGY_VALUE = 50

# Comet (Moving Obstacle) properties
COMET_SIZE_W = 20
COMET_SIZE_H = 30
COMET_MIN_SPEED = 1
COMET_MAX_SPEED = 3
INITIAL_COMETS = 5
COMET_SPAWN_RATE = 180 # Spawn einen neuen Kometen alle X Frames (z.B. alle 3 Sekunden bei 60 FPS)
MAX_COMETS_ON_SCREEN = 15 # Maximale Anzahl automatisch gespawnter Kometen gleichzeitig

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (200, 200, 0)

# Slider defaults
DEFAULT_COHESION = 0.10
DEFAULT_ALIGNMENT = 0.14
DEFAULT_SEPARATION = 0.75
DEFAULT_SPEED = 0.8
DEFAULT_AVOIDANCE = 0.5

UI_BUTTON_COLOR = (100, 180, 100)  # Ein sanftes Grün für Knöpfe
UI_BUTTON_HOVER_COLOR = (130, 210, 130) # Heller bei Hover
UI_BUTTON_TEXT_COLOR = (255, 255, 255)
UI_SLIDER_BG_COLOR = (200, 200, 200) # Hintergrund des Sliders
UI_SLIDER_BAR_COLOR = (100, 100, 220) # Farbe des ausgefüllten Teils des Sliders
UI_SLIDER_HANDLE_COLOR = (80, 80, 80)   # Farbe des Griffs
UI_TEXT_COLOR = (10, 10, 10)         # Allgemeine Textfarbe für UI