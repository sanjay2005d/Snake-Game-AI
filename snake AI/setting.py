import pygame

# Grid settings
CELL_SIZE = 20
COLS = 30
ROWS = 25

PANEL_WIDTH = 260

WINDOW_W = COLS * CELL_SIZE + PANEL_WIDTH
WINDOW_H = ROWS * CELL_SIZE

# Speed options
FPS_OPTIONS = [5, 8, 12, 16, 20, 25, 30]
DEFAULT_FPS = 3

# Colors
BG_COLOR        = (10, 10, 18)
GRID_COLOR      = (28, 28, 42)

SNAKE_HEAD_COLOR = (0, 255, 120)
SNAKE_BODY_COLOR = (0, 170, 90)

FOOD_COLOR      = (255, 80, 80)

PATH_COLOR      = (80, 160, 255)
PATH_DOT_COLOR  = (120, 200, 255)

PANEL_BG        = (14, 14, 24)
TEXT_COLOR      = (200, 200, 220)
ACCENT_COLOR    = (0, 200, 255)
WARN_COLOR      = (255, 200, 0)
DEAD_COLOR      = (255, 70, 70)

# Tab colors per algorithm
TAB_COLORS = {
    "BFS":   (0,   180, 255),
    "A*":    (80,  255, 160),
    "DFS":   (255, 140,  0),
    "GBFS":  (220,  80, 255),
}

# Algorithms
ALGO_BFS   = "BFS"
ALGO_ASTAR = "A*"
ALGO_DFS   = "DFS"
ALGO_GBFS  = "GBFS"   # Greedy Best-First Search (heuristic)

ALGO_ORDER  = [ALGO_BFS, ALGO_ASTAR, ALGO_DFS, ALGO_GBFS]
DEFAULT_ALGO = ALGO_ASTAR

# Keys
KEY_TOGGLE_ALGO    = pygame.K_TAB
KEY_TOGGLE_PATH_VIZ = pygame.K_v
KEY_SPEED_UP       = pygame.K_EQUALS
KEY_SPEED_DOWN     = pygame.K_MINUS
KEY_RESTART        = pygame.K_r
