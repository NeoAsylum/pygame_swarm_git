
# --- Konstanten ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Add/Update Shout Message Settings ---
SHOUT_DURATION = 120 # How many frames a shout lasts (e.g., 0.75 seconds)
SHOUT_CHECK_RADIUS = 50 # How far Dudes check for shouts
SHOUT_REACTION_FACTOR = 0.4 # How strongly Dudes react to shouts (push in direction)
SHOUT_ARROW_SIZE = (12, 10) # Width, Height of the arrow bounding box
SHOUT_ARROW_COLOR = (255, 255, 0) # Yellow arrow (replaces SHOUT_COLOR if you want)
SHOUT_COLOR = (255, 255, 0) # Yellow shouts
SHOUT_COOLDOWN_FRAMES = 25 # How many frames a dude must wait before shouting again
# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
DUDE_SEPARATION_RADIUS = 15.0
SEPARATION_FACTOR = 0.5
# Explosion Settings
EXPLOSION_RADIUS = 50 # Radius of the explosion effect
EXPLOSION_DURATION = 30 # How many frames the explosion lasts (e.g., 0.5 seconds at 60 FPS)

# Dude Einstellungen
DUDE_SIZE = 32
DUDE_COUNT: int = 50
DUDE_MAX_SPEED = 0.5
DUDE_NEIGHBOR_RADIUS = 70 # Wie weit Dudes andere Dudes wahrnehmen
AVOID_FACTOR = 0.2      # Stärke der Kometen-Ausweichkraft
ALIGNMENT_FACTOR = 0.03 # Stärke der Ausrichtung an Nachbarn
DUDE_HORIZONTAL_VISION_RANGE = 50 # Pixel distance on X-axis for comet detection
WANDER_STRENGTH = 0.2           # How much random horizontal force is applied each frame
EXPLOSION_RADIUS = 50 # Pixels - adjust as needed
DUDE_HEARING_RADIUS = 75 # How far Dudes "hear" shouts (pixels) - adjust as needed

# Comet Einstellungen
COMET_SIZE = 32
COMET_SPEED = 3
COMET_SPAWN_RATE = 60 # Alle X Frames einen neuen Kometen (ungefähr)
