import random
from collections import deque

from setting import COLS, ROWS, ALGO_BFS, ALGO_ASTAR, ALGO_DFS, ALGO_GBFS
from pathfinding import bfs, astar, dfs, gbfs


class Snake:

    def __init__(self, algo):
        self.body  = deque([(5, 5), (4, 5), (3, 5)])
        self.alive = True
        self.score = 0
        self.algo  = algo
        self.path  = []
        self.used_fallback = False

    @property
    def head(self):
        return self.body[0]

    def step(self, food_pos):
        blocked = set(self.body)

        if self.algo == ALGO_BFS:
            path = bfs(self.head, food_pos, blocked, COLS, ROWS)
        elif self.algo == ALGO_ASTAR:
            path = astar(self.head, food_pos, blocked, COLS, ROWS)
        elif self.algo == ALGO_DFS:
            path = dfs(self.head, food_pos, blocked, COLS, ROWS)
        else:
            path = gbfs(self.head, food_pos, blocked, COLS, ROWS)

        if len(path) > 1:
            self.used_fallback = False
            next_cell = path[1]
            self.path = path
        else:
            self.used_fallback = True
            moves = self.safe_moves()
            if not moves:
                return
            next_cell = random.choice(moves)

        self.move(next_cell, food_pos)

    def safe_moves(self):
        x, y = self.head
        options = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        safe = [(nx,ny) for nx,ny in options
                if 0<=nx<COLS and 0<=ny<ROWS and (nx,ny) not in self.body]
        if not safe:
            self.alive = False
        return safe

    def move(self, pos, food):
        if pos in self.body:
            self.alive = False
            return
        self.body.appendleft(pos)
        if pos == food:
            self.score += 1
        else:
            self.body.pop()


class Food:

    def __init__(self):
        self.position = (0, 0)

    def respawn(self, blocked):
        while True:
            x = random.randint(0, COLS-1)
            y = random.randint(0, ROWS-1)
            if (x, y) not in blocked:
                self.position = (x, y)
                return
