# --- Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 90

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UI_TEXT_COLOR = (0, 0, 0) # General UI text, distinct from comet colors

# Bird settings
INITIAL_NUM_BIRDS = 50

# --- Obstacle Settings ---
# General obstacle settings (some might be superseded by specific comet settings below)
DESIRED_NUM_OBSTACLES = 8
OBSTACLE_WIDTH = 40 # Original general obstacle width, may not be directly used by comet head
OBSTACLE_HEIGHT = 40 # Original general obstacle height, may not be directly used by comet head
OBSTACLE_SPEED = 5   # This is used as the comet's speed
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

COMET_PARTICLE_INITIAL_RADIUS = 8
COMET_PARTICLE_RADIUS_DECAY = 0.25           # Amount radius shrinks per frame
COMET_PARTICLE_INITIAL_ALPHA = 200           # Starting alpha for particles (0-255)
COMET_PARTICLE_ALPHA_DECAY = 10              # Amount alpha fades per frame
# --- End Comet Obstacle Settings ---

# Food settings
FOOD_SPAWN_INTERVAL_FRAMES = 2 # Spawn food every N frames
MAX_FOOD_ON_SCREEN = 25
FOOD_SIZE = 10 # Assuming square food

# UI and Stats
UI_FONT_SIZE = 30
UI_PADDING = 10
UI_LINE_HEIGHT = 30
STATS_UPDATE_INTERVAL_FRAMES = 30 # How often to recalculate and display average stats

# Default visual properties (likely for birds or other generic entities)
DEFAULT_COLOR = (20, 20, 20)
DEFAULT_RADIUS = 3

# Behavioral tuning constants (likely for birds)
COHESION_FORCE_DIVISOR = 10.0
SEPARATION_FORCE_MAGNITUDE = 300.0
SEPARATION_STRENGTH_DIVISOR = 30.0
FORCE_APPLICATION_SCALE = 0.03 # Scales how much forces affect velocity per update

OBSTACLE_REACTION_DISTANCE_HORIZONTAL = 200 # For bird AI
OBSTACLE_EVASION_Y_RANGE = 20               # For bird AI
OBSTACLE_VERTICAL_EVASION_MAGNITUDE = 1.5   # For bird AI
NUM_FLOCK_NEIGHBORS = 5
REPRODUCTION_THRESHOLD = 1
GLOBAL_SPEED_FACTOR= 1.5
VERTICAL_EVASION_MAGNITUDE = 1.5