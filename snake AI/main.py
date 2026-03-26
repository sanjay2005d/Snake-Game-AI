import sys
import pygame

from snake import Snake, Food

from setting import (
    CELL_SIZE, COLS, ROWS, PANEL_WIDTH,
    WINDOW_W, WINDOW_H,
    FPS_OPTIONS, DEFAULT_FPS,
    BG_COLOR, GRID_COLOR, SNAKE_HEAD_COLOR, SNAKE_BODY_COLOR,
    FOOD_COLOR, PATH_COLOR, PATH_DOT_COLOR,
    PANEL_BG, TEXT_COLOR, ACCENT_COLOR, WARN_COLOR, DEAD_COLOR,
    ALGO_BFS, ALGO_ASTAR, DEFAULT_ALGO,
    KEY_TOGGLE_ALGO, KEY_TOGGLE_PATH_VIZ,
    KEY_SPEED_UP, KEY_SPEED_DOWN, KEY_RESTART,
)


def cell_rect(x, y):
    return pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def draw_grid(surface):

    for x in range(COLS + 1):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (x * CELL_SIZE, 0),
            (x * CELL_SIZE, ROWS * CELL_SIZE)
        )

    for y in range(ROWS + 1):
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (0, y * CELL_SIZE),
            (COLS * CELL_SIZE, y * CELL_SIZE)
        )


def draw_snake(surface, snake):

    for i, cell in enumerate(snake.body):

        rect = cell_rect(*cell).inflate(-2, -2)

        if i == 0:
            color = SNAKE_HEAD_COLOR
        else:
            color = SNAKE_BODY_COLOR

        pygame.draw.rect(surface, color, rect, border_radius=4)


def draw_food(surface, food):

    x, y = food.position

    cx = x * CELL_SIZE + CELL_SIZE // 2
    cy = y * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(surface, FOOD_COLOR, (cx, cy), CELL_SIZE // 2 - 2)


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

    algo = DEFAULT_ALGO

    fps_index = DEFAULT_FPS

    snake, food = new_game(algo)

    while True:

        # EVENTS
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == KEY_RESTART:
                    snake, food = new_game(algo)

                elif event.key == KEY_TOGGLE_ALGO:

                    if algo == ALGO_BFS:
                        algo = ALGO_ASTAR
                    else:
                        algo = ALGO_BFS

                    snake.algo = algo

                elif event.key == KEY_SPEED_UP:
                    fps_index = min(fps_index + 1, len(FPS_OPTIONS) - 1)

                elif event.key == KEY_SPEED_DOWN:
                    fps_index = max(fps_index - 1, 0)

        # UPDATE
        if snake.alive:

            snake.step(food.position)

            if snake.head == food.position:

                food.respawn(set(snake.body))

        # DRAW
        screen.fill(BG_COLOR)

        draw_grid(screen)

        draw_food(screen, food)

        draw_snake(screen, snake)

        pygame.display.flip()

        clock.tick(FPS_OPTIONS[fps_index])


if __name__ == "__main__":
    main()