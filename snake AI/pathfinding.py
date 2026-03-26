from collections import deque
import heapq


def neighbors(node):
    x, y = node
    return [
        (x+1, y),
        (x-1, y),
        (x, y+1),
        (x, y-1)
    ]


def bfs(start, goal, blocked, cols, rows):

    queue = deque([start])
    parent = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for n in neighbors(current):

            x, y = n

            if x < 0 or x >= cols or y < 0 or y >= rows:
                continue

            if n in blocked:
                continue

            if n not in parent:
                parent[n] = current
                queue.append(n)

    if goal not in parent:
        return []

    path = []
    cur = goal

    while cur:
        path.append(cur)
        cur = parent[cur]

    path.reverse()
    return path


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
            break

        for n in neighbors(current):

            x, y = n

            if x < 0 or x >= cols or y < 0 or y >= rows:
                continue

            if n in blocked:
                continue

            tentative = gscore[current] + 1

            if n not in gscore or tentative < gscore[n]:

                gscore[n] = tentative
                fscore = tentative + heuristic(n, goal)

                heapq.heappush(open_set, (fscore, n))
                parent[n] = current

    if goal not in parent:
        return []

    path = []
    cur = goal

    while cur:
        path.append(cur)
        cur = parent[cur]

    path.reverse()
    return path