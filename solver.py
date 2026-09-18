from config import load_config
from collections import deque
# from mazegen import grid
from maze import generate_maze
from mazegen.constants import (DELTA, EAST, NORTH, SOUTH, WEST)

LETTERS = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}


def solve(
    grid: list[list[int]], entry: tuple[int, int], exit: tuple[int, int]
) -> str:
    """Return the shortest path from entry to exit as N/E/S/W letters."""
    came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
    queue = deque([entry])
    visited = {entry}

    while queue:
        x, y = queue.popleft()
        if (x, y) == exit:
            break
        for wall, (dx, dy) in DELTA.items():
            if grid[y][x] & wall:
                continue  # wall is closed
            nxt = (x + dx, y + dy)
            if nxt in visited:
                continue
            visited.add(nxt)
            came_from[nxt] = ((x, y), LETTERS[wall])
            queue.append(nxt)
    else:
        raise ValueError("exit is not reachable from entry")

    steps = []
    cell = exit
    while cell != entry:
        cell, letter = came_from[cell]
        steps.append(letter)
    return "".join(reversed(steps))


if __name__ == "__main__":
    config = load_config("config.txt")
    grid = generate_maze(config.width, config.height, 42)
    print(solve(grid, config.entry, config.exit))
