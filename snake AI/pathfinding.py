from collections import deque
import heapq


def neighbors(node):
    x, y = node
    return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]


def in_bounds(n, cols, rows):
    x, y = n
    return 0 <= x < cols and 0 <= y < rows


def reconstruct(parent, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


# ── BFS ──────────────────────────────────────────────────────────────────────
def bfs(start, goal, blocked, cols, rows):
    queue  = deque([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()
        if current == goal:
            return reconstruct(parent, goal)
        for n in neighbors(current):
            if not in_bounds(n, cols, rows): continue
            if n in blocked:                 continue
            if n in parent:                  continue
            parent[n] = current
            queue.append(n)
    return []


# ── A* ───────────────────────────────────────────────────────────────────────
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


def astar(start, goal, blocked, cols, rows):
    open_set = []
    heapq.heappush(open_set, (0, start))
    parent = {start: None}
    gscore = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct(parent, goal)
        for n in neighbors(current):
            if not in_bounds(n, cols, rows): continue
            if n in blocked:                 continue
            tentative = gscore[current] + 1
            if n not in gscore or tentative < gscore[n]:
                gscore[n] = tentative
                parent[n] = current
                heapq.heappush(open_set, (tentative + heuristic(n, goal), n))
    return []


# ── DFS (greedy neighbour ordering) ──────────────────────────────────────────
def dfs(start, goal, blocked, cols, rows):
    stack  = [start]
    parent = {start: None}

    while stack:
        current = stack.pop()
        if current == goal:
            return reconstruct(parent, goal)

        nbs = []
        for n in neighbors(current):
            if not in_bounds(n, cols, rows): continue
            if n in blocked:                 continue
            if n in parent:                  continue
            dist = heuristic(n, goal)
            nbs.append((dist, n))

        # push farthest first → closest gets popped first
        nbs.sort(reverse=True)
        for _, n in nbs:
            parent[n] = current
            stack.append(n)
    return []


# ── Greedy Best-First Search (pure heuristic) ─────────────────────────────────
def gbfs(start, goal, blocked, cols, rows):
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))
    parent = {start: None}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            return reconstruct(parent, goal)
        for n in neighbors(current):
            if not in_bounds(n, cols, rows): continue
            if n in blocked:                 continue
            if n in parent:                  continue
            parent[n] = current
            heapq.heappush(open_set, (heuristic(n, goal), n))
    return []
