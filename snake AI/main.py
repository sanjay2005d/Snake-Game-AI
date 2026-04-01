import sys
import math
import pygame

from snake import Snake, Food
from setting import (
    CELL_SIZE, COLS, ROWS, PANEL_WIDTH,
    WINDOW_W, WINDOW_H,
    FPS_OPTIONS, DEFAULT_FPS,
    BG_COLOR, GRID_COLOR, SNAKE_HEAD_COLOR, SNAKE_BODY_COLOR,
    FOOD_COLOR, PANEL_BG, TEXT_COLOR, ACCENT_COLOR,
    ALGO_BFS, ALGO_ASTAR, ALGO_DFS, ALGO_GBFS,
    ALGO_ORDER, DEFAULT_ALGO,
    TAB_COLORS,
    KEY_TOGGLE_ALGO, KEY_SPEED_UP, KEY_SPEED_DOWN, KEY_RESTART,
)

# ── per-algo stats ────────────────────────────────────────────────────────────
stats = {a: {"food": 0, "steps": 0, "best": 0} for a in ALGO_ORDER}

ALGO_DESC = {
    ALGO_BFS:  ["Explores ALL neighbours", "level by level.",
                "Guarantees SHORTEST path.", "Slow on large grids."],
    ALGO_ASTAR:["Uses Manhattan distance", "heuristic + path cost.",
                "Optimal AND efficient.", "Best all-round choice."],
    ALGO_DFS:  ["Explores DEEP first.", "Greedy neighbour order.",
                "Fast but NOT optimal.", "Path can be long."],
    ALGO_GBFS: ["Pure heuristic search.", "Ignores path cost.",
                "Very fast to find food.", "Not guaranteed optimal."],
}

# ── helpers ───────────────────────────────────────────────────────────────────
def cell_rect(x, y):
    return pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def draw_grid(surface):
    for x in range(COLS + 1):
        pygame.draw.line(surface, GRID_COLOR,
                         (x*CELL_SIZE, 0), (x*CELL_SIZE, ROWS*CELL_SIZE))
    for y in range(ROWS + 1):
        pygame.draw.line(surface, GRID_COLOR,
                         (0, y*CELL_SIZE), (COLS*CELL_SIZE, y*CELL_SIZE))


def draw_path(surface, snake, algo):
    if not snake.path:
        return
    color = TAB_COLORS[algo]
    for i, cell in enumerate(snake.path[1:], 1):
        t = i / max(len(snake.path)-1, 1)
        c = lerp_color(color, (30, 30, 50), t)
        rect = cell_rect(*cell).inflate(-12, -12)
        pygame.draw.rect(surface, c, rect, border_radius=4)


def draw_snake(surface, snake, algo):
    head_color = TAB_COLORS[algo]
    body_color = lerp_color(TAB_COLORS[algo], (10, 10, 20), 0.6)

    for i, cell in enumerate(snake.body):
        rect = cell_rect(*cell).inflate(-2, -2)
        color = head_color if i == 0 else body_color
        pygame.draw.rect(surface, color, rect, border_radius=5)

        # subtle inner glow on head
        if i == 0:
            inner = rect.inflate(-6, -6)
            glow = lerp_color(head_color, (255,255,255), 0.4)
            pygame.draw.rect(surface, glow, inner, border_radius=3)

    # eyes
    hx, hy = snake.body[0]
    cx = hx*CELL_SIZE + CELL_SIZE//2
    cy = hy*CELL_SIZE + CELL_SIZE//2
    pygame.draw.circle(surface, (0,0,0), (cx-4, cy-4), 3)
    pygame.draw.circle(surface, (0,0,0), (cx+4, cy-4), 3)
    pygame.draw.circle(surface, (255,255,255), (cx-3, cy-5), 1)
    pygame.draw.circle(surface, (255,255,255), (cx+5, cy-5), 1)


def draw_food(surface, food, tick):
    x, y = food.position
    cx = x*CELL_SIZE + CELL_SIZE//2
    cy = y*CELL_SIZE + CELL_SIZE//2
    pulse = abs(math.sin(tick * 0.05)) * 3
    pygame.draw.circle(surface, (180, 30, 30), (cx, cy), int(CELL_SIZE//2 - 1 + pulse))
    pygame.draw.circle(surface, FOOD_COLOR,   (cx, cy), int(CELL_SIZE//2 - 3 + pulse))
    pygame.draw.circle(surface, (255,200,200),(cx-2, cy-3), 2)


# ── TAB BAR ───────────────────────────────────────────────────────────────────
TAB_H    = 44
TAB_W    = PANEL_WIDTH // len(ALGO_ORDER)

def draw_tabs(surface, font_tab, algo):
    px = COLS * CELL_SIZE
    # tab bar background
    pygame.draw.rect(surface, (8, 8, 16), (px, 0, PANEL_WIDTH, TAB_H))

    for i, a in enumerate(ALGO_ORDER):
        tx  = px + i * TAB_W
        col = TAB_COLORS[a]
        active = (a == algo)

        # tab background
        bg = col if active else (20, 20, 32)
        pygame.draw.rect(surface, bg, (tx, 0, TAB_W, TAB_H))

        # top accent bar
        pygame.draw.rect(surface, col if active else (40,40,60),
                         (tx, 0, TAB_W, 3))

        # divider
        pygame.draw.line(surface, (40,40,60), (tx, 0), (tx, TAB_H))

        # label
        tc = (0,0,0) if active else col
        lbl = font_tab.render(a, True, tc)
        lx  = tx + (TAB_W - lbl.get_width()) // 2
        ly  = (TAB_H - lbl.get_height()) // 2
        surface.blit(lbl, (lx, ly))

    # bottom border
    pygame.draw.line(surface, (40,40,60),
                     (px, TAB_H), (px+PANEL_WIDTH, TAB_H))


# ── SIDE PANEL ────────────────────────────────────────────────────────────────
def draw_panel(surface, fonts, snake, algo, fps, tick):
    font_sm, font_md, font_lg, font_tab = fonts
    px  = COLS * CELL_SIZE
    col = TAB_COLORS[algo]

    # background
    pygame.draw.rect(surface, PANEL_BG, (px, TAB_H, PANEL_WIDTH, WINDOW_H - TAB_H))

    # subtle left border glow
    for i in range(4):
        alpha_surf = pygame.Surface((2, WINDOW_H - TAB_H), pygame.SRCALPHA)
        alpha_surf.fill((*col, 60 - i*15))
        surface.blit(alpha_surf, (px + i, TAB_H))

    y = TAB_H + 18

    # ── algo name big ────────────────────────────────────────────────────────
    name_surf = font_lg.render(algo, True, col)
    surface.blit(name_surf, (px + 20, y))
    y += name_surf.get_height() + 4

    # full name subtitle
    full = {"BFS": "Breadth-First Search", "A*": "A-Star Search",
            "DFS": "Depth-First Search",   "GBFS": "Greedy Best-First"}
    sub = font_sm.render(full[algo], True, (120,120,150))
    surface.blit(sub, (px + 22, y))
    y += 26

    # divider
    pygame.draw.line(surface, (40,40,60), (px+16, y), (px+PANEL_WIDTH-16, y))
    y += 14

    # ── score card ───────────────────────────────────────────────────────────
    card_rect = pygame.Rect(px+14, y, PANEL_WIDTH-28, 64)
    pygame.draw.rect(surface, (18,18,30), card_rect, border_radius=8)
    pygame.draw.rect(surface, col, card_rect, 1, border_radius=8)

    sc = font_lg.render(str(snake.score), True, col)
    surface.blit(sc, (px + 26, y + 8))
    sl = font_sm.render("SCORE", True, (100,100,130))
    surface.blit(sl, (px + 26, y + 8 + sc.get_height()))

    ln = font_lg.render(str(len(snake.body)), True, (180,180,220))
    surface.blit(ln, (px + PANEL_WIDTH//2 + 10, y + 8))
    ll = font_sm.render("LENGTH", True, (100,100,130))
    surface.blit(ll, (px + PANEL_WIDTH//2 + 10, y + 8 + ln.get_height()))

    y += 80

    # ── description ──────────────────────────────────────────────────────────
    for line in ALGO_DESC[algo]:
        t = font_sm.render(line, True, (160,160,190))
        surface.blit(t, (px+20, y))
        y += 20
    y += 8

    # divider
    pygame.draw.line(surface, (40,40,60), (px+16, y), (px+PANEL_WIDTH-16, y))
    y += 14

    # ── session stats for THIS algo ──────────────────────────────────────────
    st = stats[algo]
    header = font_sm.render("SESSION STATS", True, (100,100,130))
    surface.blit(header, (px+20, y))
    y += 20

    rows_data = [
        ("Food eaten",  str(st["food"])),
        ("Steps taken", str(st["steps"])),
        ("Best score",  str(st["best"])),
    ]
    for label, val in rows_data:
        lsurf = font_sm.render(label, True, (140,140,170))
        vsurf = font_sm.render(val,   True, col)
        surface.blit(lsurf, (px+20,  y))
        surface.blit(vsurf, (px+PANEL_WIDTH-20-vsurf.get_width(), y))
        y += 22
    y += 6

    # divider
    pygame.draw.line(surface, (40,40,60), (px+16, y), (px+PANEL_WIDTH-16, y))
    y += 14

    # ── speed bar ────────────────────────────────────────────────────────────
    spd_lbl = font_sm.render(f"SPEED  {fps} FPS", True, (140,140,170))
    surface.blit(spd_lbl, (px+20, y))
    y += 20
    bar_w = PANEL_WIDTH - 32
    bar_fill = int(bar_w * (FPS_OPTIONS.index(fps) / (len(FPS_OPTIONS)-1)))
    pygame.draw.rect(surface, (30,30,46), (px+16, y, bar_w, 6), border_radius=3)
    pygame.draw.rect(surface, col,        (px+16, y, bar_fill, 6), border_radius=3)
    y += 22

    # divider
    pygame.draw.line(surface, (40,40,60), (px+16, y), (px+PANEL_WIDTH-16, y))
    y += 14

    # ── controls ─────────────────────────────────────────────────────────────
    ctrl_lbl = font_sm.render("CONTROLS", True, (100,100,130))
    surface.blit(ctrl_lbl, (px+20, y))
    y += 20

    controls = [
        ("TAB",   "Switch algorithm"),
        ("+ / -", "Change speed"),
        ("R",     "Restart game"),
    ]
    for key, desc in controls:
        k = font_sm.render(key,  True, col)
        d = font_sm.render(desc, True, (150,150,180))
        # key badge
        badge = pygame.Rect(px+16, y-2, k.get_width()+10, k.get_height()+4)
        pygame.draw.rect(surface, (28,28,44), badge, border_radius=4)
        pygame.draw.rect(surface, col, badge, 1, border_radius=4)
        surface.blit(k, (px+21, y))
        surface.blit(d, (px+16+badge.width+8, y))
        y += 24

    # ── fallback indicator ───────────────────────────────────────────────────
    if snake.used_fallback:
        y += 8
        fb = font_sm.render("⚠ NO PATH — random move", True, (255,180,0))
        surface.blit(fb, (px+20, y))


# ── GAME OVER SCREEN ──────────────────────────────────────────────────────────
def draw_game_over(surface, fonts, algo):
    font_sm, font_md, font_lg, font_tab = fonts

    overlay = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 8, 210))
    surface.blit(overlay, (0, 0))

    cx = (COLS * CELL_SIZE) // 2

    # title
    title = font_lg.render("GAME  OVER", True, (255, 60, 60))
    surface.blit(title, (cx - title.get_width()//2, 60))

    # subtitle
    sub = font_md.render("Algorithm Comparison", True, (180,180,220))
    surface.blit(sub, (cx - sub.get_width()//2, 120))

    # table
    y = 165
    col_w = (COLS * CELL_SIZE - 40) // 4
    headers = ["ALGO", "FOOD", "STEPS", "BEST"]
    hx = 20
    for h in headers:
        hs = font_sm.render(h, True, (120,120,150))
        surface.blit(hs, (hx, y))
        hx += col_w
    y += 22

    pygame.draw.line(surface, (60,60,80), (20, y), (COLS*CELL_SIZE-20, y))
    y += 10

    best_food = max(stats[a]["food"] for a in ALGO_ORDER)

    for a in ALGO_ORDER:
        st   = stats[a]
        col  = TAB_COLORS[a]
        is_best = (st["food"] == best_food and best_food > 0)

        rx = 20
        # row highlight if best
        if is_best:
            pygame.draw.rect(surface, (20,20,40),
                             (16, y-4, COLS*CELL_SIZE-32, 26), border_radius=4)
            pygame.draw.rect(surface, col,
                             (16, y-4, COLS*CELL_SIZE-32, 26), 1, border_radius=4)

        for val in [a, str(st["food"]), str(st["steps"]), str(st["best"])]:
            c = col if is_best else (180,180,210)
            vs = font_sm.render(val, True, c)
            surface.blit(vs, (rx, y))
            rx += col_w

        if is_best:
            star = font_sm.render("★ WINNER", True, col)
            surface.blit(star, (rx - col_w//2, y))
        y += 30

    y += 10
    restart = font_md.render("Press  R  to Restart", True, (200,200,230))
    surface.blit(restart, (cx - restart.get_width()//2, y))


# ── MAIN ─────────────────────────────────────────────────────────────────────
def new_game(algo):
    snake = Snake(algo=algo)
    food  = Food()
    food.respawn(set(snake.body))
    return snake, food


def main():
    pygame.init()
    pygame.display.set_caption("Snake AI  —  BFS  |  A*  |  DFS  |  GBFS")
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    clock  = pygame.time.Clock()

    # fonts
    font_sm  = pygame.font.SysFont("consolas", 13)
    font_md  = pygame.font.SysFont("consolas", 18, bold=True)
    font_lg  = pygame.font.SysFont("consolas", 26, bold=True)
    font_tab = pygame.font.SysFont("consolas", 14, bold=True)
    fonts    = (font_sm, font_md, font_lg, font_tab)

    algo      = DEFAULT_ALGO
    fps_index = DEFAULT_FPS
    snake, food = new_game(algo)
    tick = 0

    while True:

        # ── EVENTS ───────────────────────────────────────────────────────────
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == KEY_RESTART:
                    snake, food = new_game(algo)

                elif event.key == KEY_TOGGLE_ALGO:
                    idx  = ALGO_ORDER.index(algo)
                    algo = ALGO_ORDER[(idx + 1) % len(ALGO_ORDER)]
                    snake.algo = algo

                elif event.key == KEY_SPEED_UP:
                    fps_index = min(fps_index + 1, len(FPS_OPTIONS) - 1)

                elif event.key == KEY_SPEED_DOWN:
                    fps_index = max(fps_index - 1, 0)

            # click on tabs
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                px = COLS * CELL_SIZE
                if px <= mx <= px + PANEL_WIDTH and 0 <= my <= TAB_H:
                    ti = (mx - px) // TAB_W
                    if 0 <= ti < len(ALGO_ORDER):
                        algo = ALGO_ORDER[ti]
                        snake.algo = algo

        # ── UPDATE ───────────────────────────────────────────────────────────
        if snake.alive:
            snake.step(food.position)
            stats[algo]["steps"] += 1

            if snake.head == food.position:
                stats[algo]["food"] += 1
                stats[algo]["best"] = max(stats[algo]["best"], snake.score)
                food.respawn(set(snake.body))

        tick += 1

        # ── DRAW ─────────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        draw_grid(screen)
        draw_food(screen, food, tick)
        draw_path(screen, snake, algo)
        draw_snake(screen, snake, algo)
        draw_tabs(screen, font_tab, algo)
        draw_panel(screen, fonts, snake, algo, FPS_OPTIONS[fps_index], tick)

        if not snake.alive:
            draw_game_over(screen, fonts, algo)

        pygame.display.flip()
        clock.tick(FPS_OPTIONS[fps_index])


if __name__ == "__main__":
    main()
