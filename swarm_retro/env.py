# --- Constants ---
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000
FPS = 120 # Target FPS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UI_TEXT_COLOR = (0, 0, 0)

# Bird settings
INITIAL_NUM_BIRDS = 50

# Obstacle settings
DESIRED_NUM_OBSTACLES = 8
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 30
OBSTACLE_SPEED = 4
# Condition to spawn more obstacles if bird count is high (gameplay mechanic)
OBSTACLE_HIGH_BIRD_THRESHOLD = 120

# Food settings
FOOD_SPAWN_INTERVAL_FRAMES = 2 # Spawn food every N frames
MAX_FOOD_ON_SCREEN = 30
FOOD_SIZE = 10 # Assuming square food

# UI and Stats
UI_FONT_SIZE = 30
UI_PADDING = 10
UI_LINE_HEIGHT = 30
STATS_UPDATE_INTERVAL_FRAMES = 30 # How often to recalculate and display average stats
