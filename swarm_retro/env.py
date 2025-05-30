# --- Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 90

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UI_TEXT_COLOR = (0, 0, 0)

# Bird settings
INITIAL_NUM_BIRDS = 50

# Obstacle settings
DESIRED_NUM_OBSTACLES = 8
OBSTACLE_WIDTH = 40
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED = 5
# Condition to spawn more obstacles if bird count is high (gameplay mechanic)
OBSTACLE_HIGH_BIRD_THRESHOLD = 120

# Food settings
FOOD_SPAWN_INTERVAL_FRAMES = 2 # Spawn food every N frames
MAX_FOOD_ON_SCREEN = 25
FOOD_SIZE = 10 # Assuming square food

# UI and Stats
UI_FONT_SIZE = 30
UI_PADDING = 10
UI_LINE_HEIGHT = 30
STATS_UPDATE_INTERVAL_FRAMES = 30 # How often to recalculate and display average stats
# Default visual properties (can be overridden by instance parameters if needed)
DEFAULT_COLOR = (20, 20, 20)
DEFAULT_RADIUS = 3

# Behavioral tuning constants (consider moving to __init__ if they need to be instance-specific from the start)
# Or if they are truly global for all birds, class attributes are fine.
COHESION_FORCE_DIVISOR = 10.0
SEPARATION_FORCE_MAGNITUDE = 300.0
SEPARATION_STRENGTH_DIVISOR = 30.0
FORCE_APPLICATION_SCALE = 0.03 # Scales how much forces affect velocity per update

OBSTACLE_REACTION_DISTANCE_HORIZONTAL = 200
OBSTACLE_EVASION_Y_RANGE = 20
OBSTACLE_VERTICAL_EVASION_MAGNITUDE = 1.5
NUM_FLOCK_NEIGHBORS = 5
REPRODUCTION_THRESHOLD = 1
GLOBAL_SPEED_FACTOR= 1.5
VERTICAL_EVASION_MAGNITUDE = 1.5