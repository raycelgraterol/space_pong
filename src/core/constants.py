"""
Space Pong - Game Constants
Todas las constantes del juego centralizadas
"""

# =============================================================================
# DISPLAY
# =============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Space Pong - Tenis Espacial"

# =============================================================================
# COLORS (RGB)
# =============================================================================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Colores del espacio
SPACE_BLACK = (10, 10, 25)
STAR_WHITE = (255, 255, 240)
LASER_RED = (255, 50, 50)
LASER_GLOW = (255, 100, 100)

# UI Colors
UI_PRIMARY = (100, 150, 255)
UI_SECONDARY = (80, 120, 200)
UI_HIGHLIGHT = (150, 200, 255)
UI_TEXT = (220, 220, 240)

# =============================================================================
# GAME MECHANICS
# =============================================================================
# Velocidades
SHIP_SPEED = 400  # pixeles por segundo
BALL_INITIAL_SPEED = 350  # pixeles por segundo
BALL_MAX_SPEED = 700  # pixeles por segundo
BALL_SPEED_INCREMENT = 1.05  # multiplicador por cada golpe (5% incremento)

# Dimensiones de entidades
SHIP_WIDTH = 80
SHIP_HEIGHT = 100
BALL_SIZE = 40
LASER_GRID_WIDTH = 10
LASER_GRID_HEIGHT = SCREEN_HEIGHT

# Posiciones
SHIP_MARGIN = 50  # distancia del borde de pantalla
SHIP_P1_X = SHIP_MARGIN
SHIP_P2_X = SCREEN_WIDTH - SHIP_MARGIN - SHIP_WIDTH

# Física
MAX_BOUNCE_ANGLE = 60  # grados máximos de rebote
WALL_BOUNCE_VARIATION = 5  # variación aleatoria en rebote de pared (pixeles)

# =============================================================================
# SCORING
# =============================================================================
WINNING_SCORE = 10
LASER_TOUCH_PENALTY = 1  # puntos que gana el oponente si tocas el láser

# =============================================================================
# AI DIFFICULTY SETTINGS
# =============================================================================
AI_DIFFICULTY = {
    'easy': {
        'reaction_delay': 0.3,  # segundos - reaccion lenta
        'prediction_error': 120,  # pixeles - muy impreciso
        'speed_multiplier': 0.6,
        'mistake_chance': 0.4,
        'focus_drift': 0.8,  # 80% de desenfoque aleatorio
        'drift_speed': 4.0 # velocidad del desenfoque
    },
    'medium': {
        'reaction_delay': 0.15,
        'prediction_error': 60,  # pixeles
        'speed_multiplier': 0.8,
        'mistake_chance': 0.2,
        'focus_drift': 0.4,  # 40% de desenfoque
        'drift_speed': 2.0
    },
    'hard': {
        'reaction_delay': 0.05,
        'prediction_error': 15,
        'speed_multiplier': 1.0,
        'mistake_chance': 0.05,
        'focus_drift': 0.1,  # 10% de desenfoque
        'drift_speed': 1.0
    }
}

# =============================================================================
# CONTROLS
# =============================================================================
import pygame

CONTROLS = {
    'player1': {
        'up': [pygame.K_w],
        'down': [pygame.K_s]
    },
    'player2': {
        'up': [pygame.K_UP],
        'down': [pygame.K_DOWN]
    },
    'general': {
        'pause': [pygame.K_ESCAPE, pygame.K_p],
        'confirm': [pygame.K_RETURN, pygame.K_SPACE],
        'back': [pygame.K_ESCAPE, pygame.K_BACKSPACE]
    }
}

# =============================================================================
# GAME STATES
# =============================================================================
class GameState:
    MENU = 'menu'
    SHIP_SELECT = 'ship_select'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'

# =============================================================================
# GAME MODES
# =============================================================================
class GameMode:
    PVP = 'pvp'  # Player vs Player
    PVE = 'pve'  # Player vs Bot

# =============================================================================
# ASSET PATHS
# =============================================================================
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent.parent / 'assets'
IMAGES_DIR = ASSETS_DIR / 'images'
SOUNDS_DIR = ASSETS_DIR / 'sounds'
FONTS_DIR = ASSETS_DIR / 'fonts'

# Sprites
SHIPS_DIR = IMAGES_DIR / 'ships'
BALL_DIR = IMAGES_DIR / 'ball'
EFFECTS_DIR = IMAGES_DIR / 'effects'
BACKGROUNDS_DIR = IMAGES_DIR / 'backgrounds'
