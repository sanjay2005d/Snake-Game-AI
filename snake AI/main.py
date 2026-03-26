import sys
import pygame

from snake import Snake, Food

from setting import (
    CELL_SIZE, COLS, ROWS, PANEL_WIDTH,
    WINDOW_W, WINDOW_H,
    FPS_OPTIONS, DEFAULT_FPS,
    BG_COLOR, GRID_COLOR, SNAKE_HEAD_COLOR, SNAKE_BODY_COLOR,
    FOOD_COLOR,
    PANEL_BG, TEXT_COLOR, ACCENT_COLOR,
    ALGO_BFS, ALGO_ASTAR, DEFAULT_ALGO,
    KEY_TOGGLE_ALGO,
    KEY_SPEED_UP, KEY_SPEED_DOWN, KEY_RESTART,
)

def draw_path(surface, snake):

    if not snake.path:
        return

    for cell in snake.path:

        x, y = cell

        rect = cell_rect(x, y).inflate(-10, -10)

        pygame.draw.rect(surface, (100, 200, 255), rect, border_radius=3)
def cell_rect(x, y):
    return pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def draw_grid(surface):

    for x in range(COLS + 1):
        pygame.draw.line(surface, GRID_COLOR,
                         (x * CELL_SIZE, 0),
                         (x * CELL_SIZE, ROWS * CELL_SIZE))

    for y in range(ROWS + 1):
        pygame.draw.line(surface, GRID_COLOR,
                         (0, y * CELL_SIZE),
                         (COLS * CELL_SIZE, y * CELL_SIZE))


def draw_snake(surface, snake):

    for i, cell in enumerate(snake.body):

        rect = cell_rect(*cell).inflate(-2, -2)

        color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR

        pygame.draw.rect(surface, color, rect, border_radius=4)

    # Snake eyes
    hx, hy = snake.body[0]

    cx = hx * CELL_SIZE + CELL_SIZE // 2
    cy = hy * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(surface, BG_COLOR, (cx - 4, cy - 4), 2)
    pygame.draw.circle(surface, BG_COLOR, (cx + 4, cy - 4), 2)


def draw_food(surface, food):

    x, y = food.position

    cx = x * CELL_SIZE + CELL_SIZE // 2
    cy = y * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(surface, FOOD_COLOR, (cx, cy), CELL_SIZE // 2 - 2)


def draw_panel(surface, font, snake, algo, fps):

    panel_x = COLS * CELL_SIZE

    pygame.draw.rect(surface, PANEL_BG,
                     (panel_x, 0, PANEL_WIDTH, WINDOW_H))

    y = 20

    lines = [
        "SNAKE AI",
        "",
        f"Score: {snake.score}",
        f"Length: {len(snake.body)}",
        "",
        f"Algorithm: {algo}",
        "",
        "BFS → explores all nodes",
        "A*  → heuristic search",
        "",
        f"Speed: {fps} FPS",
        "",
        "Controls",
        "TAB → Switch Algo",
        "+ / - → Speed",
        "R → Restart"
    ]

    for line in lines:

        color = ACCENT_COLOR if "Algorithm" in line else TEXT_COLOR

        text = font.render(line, True, color)

        surface.blit(text, (panel_x + 20, y))

        y += 28


def draw_game_over(surface, bfs_food, astar_food, bfs_steps, astar_steps):

    overlay = pygame.Surface((WINDOW_W, WINDOW_H))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))

    surface.blit(overlay, (0, 0))

    big_font = pygame.font.SysFont("arial", 50)
    font = pygame.font.SysFont("arial", 25)

    title = big_font.render("GAME OVER", True, (255, 60, 60))
    surface.blit(title, (WINDOW_W//2 - title.get_width()//2, 80))

    y = 200

    lines = [
        "Algorithm Comparison",
        "",
        f"BFS  → Steps: {bfs_steps} | Food: {bfs_food}",
        f"A*   → Steps: {astar_steps} | Food: {astar_food}",
        ""
    ]

    if astar_food > bfs_food:
        lines.append("Better Algorithm: A*")
    elif bfs_food > astar_food:
        lines.append("Better Algorithm: BFS")
    else:
        lines.append("Both performed equally")

    lines.append("")
    lines.append("Press R to Restart")

    for line in lines:

        text = font.render(line, True, (255,255,255))

        surface.blit(text, (WINDOW_W//2 - 180, y))

        y += 35


def new_game(algo):

    snake = Snake(algo=algo)

    food = Food()

    food.respawn(set(snake.body))

    return snake, food


def main():

    pygame.init()

    pygame.display.set_caption("Snake AI — BFS & A*")

    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))

    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 20)

    algo = DEFAULT_ALGO

    fps_index = DEFAULT_FPS

    snake, food = new_game(algo)

    # Algorithm statistics
    bfs_food = 0
    astar_food = 0
    bfs_steps = 0
    astar_steps = 0

    while True:

        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == KEY_RESTART:
                    snake, food = new_game(algo)
                    bfs_food = astar_food = bfs_steps = astar_steps = 0

                elif event.key == KEY_TOGGLE_ALGO:

                    algo = ALGO_BFS if algo == ALGO_ASTAR else ALGO_ASTAR
                    snake.algo = algo

                elif event.key == KEY_SPEED_UP:
                    fps_index = min(fps_index + 1, len(FPS_OPTIONS) - 1)

                elif event.key == KEY_SPEED_DOWN:
                    fps_index = max(fps_index - 1, 0)

        # UPDATE
        if snake.alive:

            snake.step(food.position)

            if snake.algo == ALGO_BFS:
                bfs_steps += 1
            else:
                astar_steps += 1

            if snake.head == food.position:

                if snake.algo == ALGO_BFS:
                    bfs_food += 1
                else:
                    astar_food += 1

                food.respawn(set(snake.body))

        # DRAW
        screen.fill(BG_COLOR)

        draw_grid(screen)

        draw_food(screen, food)

        draw_path(screen, snake)

        draw_snake(screen, snake)

        draw_panel(screen, font, snake, algo, FPS_OPTIONS[fps_index])

        if not snake.alive:
            draw_game_over(screen, bfs_food, astar_food, bfs_steps, astar_steps)

        pygame.display.flip()

        clock.tick(FPS_OPTIONS[fps_index])


if __name__ == "__main__":
    main()
