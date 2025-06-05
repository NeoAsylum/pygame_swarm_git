# --- Constants ---
SCREEN_WIDTH = 1700
SCREEN_HEIGHT = 800
FPS = 90

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Bird settings
INITIAL_NUM_BIRDS = 50

# --- Obstacle Settings ---
DESIRED_NUM_OBSTACLES = 7
OBSTACLE_SPEED = 4   # This is used as the comet's speed
OBSTACLE_HIGH_BIRD_THRESHOLD = 120 # Condition to spawn more obstacles

# --- Comet Obstacle Specific Settings (Black/Red Theme) ---
COMET_HEAD_WIDTH = 35
COMET_HEAD_HEIGHT = 35
COMET_HEAD_CORE_COLOR = (40, 0, 0, 255)      # Dark, almost black-red core
COMET_HEAD_GLOW_COLOR = (200, 0, 0, 120)     # Semi-transparent fiery red glow

COMET_TRAIL_MAX_PARTICLES = 25
COMET_TRAIL_SPAWN_INTERVAL = 1               # Spawn a particle every N frames
COMET_TRAIL_RENDER_WIDTH = 150               # Max visual length of trail on sprite surface
COMET_TRAIL_PARTICLE_COLOR = (230, 40, 0)    # Fiery red/orange trail particles (RGB only, alpha is dynamic)

COMET_PARTICLE_INITIAL_RADIUS = 12
COMET_PARTICLE_RADIUS_DECAY = 0.25           # Amount radius shrinks per frame
COMET_PARTICLE_INITIAL_ALPHA = 200           # Starting alpha for particles (0-255)
COMET_PARTICLE_ALPHA_DECAY = 10              # Amount alpha fades per frame

# Food settings
FOOD_SPAWN_INTERVAL_FRAMES = 1 # Spawn food every N frames
MAX_FOOD_ON_SCREEN = 120
FOOD_SIZE = 5 # Assuming square food

# UI and Stats
UI_FONT_SIZE = 30
UI_PADDING = 10
UI_LINE_HEIGHT = 30
STATE_UPDATE_INTERVAL_FRAMES = 50 # How often to recalculate and display average stats
STATS_UPDATE_INTERVAL_FRAMES = 100 # How often to recalculate and display average stats

DEFAULT_RADIUS = 3

OBSTACLE_REACTION_DISTANCE_HORIZONTAL = 200
OBSTACLE_VERTICAL_EVASION_MAGNITUDE = 1.5
NUM_FLOCK_NEIGHBORS = 5
REPRODUCTION_THRESHOLD = 2
GLOBAL_SPEED_FACTOR= 2.2
