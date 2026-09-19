"""Reusable maze generation.

Example:
    generator = MazeGenerator(20, 15, seed=42)
    grid = generator.generate()
    path = generator.solution_path((0, 0), (19, 14))

Use ``blocked_cells`` for cells that must stay fully closed, such as a visual
pattern. Blocked cells cannot be used as a path's entry or exit.
"""

import random
from collections import deque
from collections.abc import Iterable, Iterator

from .constants import ALL_WALLS, DELTA, EAST, NORTH, OPPOSITE, SOUTH, WEST

Coordinate = tuple[int, int]
Grid = list[list[int]]

__all__ = [
    "ALL_WALLS",
    "EAST",
    "NORTH",
    "SOUTH",
    "WEST",
    "Grid",
    "MazeGenerator",
]

_DIRECTIONS: tuple[tuple[int, int, int], ...] = (
    (0, -1, NORTH),
    (1, 0, EAST),
    (0, 1, SOUTH),
    (-1, 0, WEST),
)
_PATH_LETTERS: dict[int, str] = {
    NORTH: "N",
    EAST: "E",
    SOUTH: "S",
    WEST: "W",
}


class MazeGenerator:
    """Generate mazes and expose their wall grid and shortest paths.

    Args:
        width: Number of columns.
        height: Number of rows.
        seed: Optional seed used for reproducible generation.
        perfect: Whether to leave the active maze as a spanning tree.
        blocked_cells: Coordinates that remain fully closed and unconnected.

    Each cell in :attr:`grid` is a wall bitmask: North, East, South, and West
    use bits 0 through 3 respectively. Call :meth:`generate` before accessing
    a solution.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: int | str | None = None,
        perfect: bool = True,
        blocked_cells: Iterable[Coordinate] | None = None,
    ) -> None:
        """Initialize the generator and validate its reusable parameters."""
        if width < 1 or height < 1:
            raise ValueError("Maze dimensions must be positive.")
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self.blocked_cells = frozenset(blocked_cells or ())
        if any(not self._in_bounds(x, y) for x, y in self.blocked_cells):
            raise ValueError("Blocked cells must be inside the maze bounds.")
        if len(self.blocked_cells) == width * height:
            raise ValueError("At least one maze cell must not be blocked.")
        self.grid: Grid = []

    def generate(self) -> Grid:
        """Generate and return a connected maze for all non-blocked cells."""
        self.grid = [
            [ALL_WALLS for _ in range(self.width)] for _ in range(self.height)
        ]
        rng = random.Random(self.seed)
        start = next(self._active_cells())
        visited: set[Coordinate] = {start}
        stack: list[Coordinate] = [start]

        while stack:
            x, y = stack[-1]
            choices: list[tuple[int, int, int]] = []
            for dx, dy, wall in _DIRECTIONS:
                nx, ny = x + dx, y + dy
                if self._is_active(nx, ny) and (nx, ny) not in visited:
                    choices.append((nx, ny, wall))
            if not choices:
                stack.pop()
                continue

            nx, ny, wall = rng.choice(choices)
            self._open_wall(x, y, nx, ny, wall)
            visited.add((nx, ny))
            stack.append((nx, ny))

        active_count = self.width * self.height - len(self.blocked_cells)
        if len(visited) != active_count:
            raise ValueError("Blocked cells divide the maze into regions.")
        if not self.perfect:
            self._add_extra_passages(rng)
        return self.grid

    def solution_path(self, entry: Coordinate, exit_: Coordinate) -> str:
        """Return a shortest N/E/S/W path between two generated maze cells.

        Raises:
            ValueError: If generation has not run or a coordinate is unusable.
        """
        if not self.grid:
            raise ValueError("Generate a maze before requesting a solution.")
        if not self._is_active(*entry) or not self._is_active(*exit_):
            raise ValueError("Entry and exit must be non-blocked maze cells.")

        queue: deque[Coordinate] = deque([entry])
        visited: set[Coordinate] = {entry}
        came_from: dict[Coordinate, tuple[Coordinate, str]] = {}
        while queue:
            x, y = queue.popleft()
            if (x, y) == exit_:
                break
            for wall, (dx, dy) in DELTA.items():
                nx, ny = x + dx, y + dy
                if self.grid[y][x] & wall or not self._is_active(nx, ny):
                    continue
                next_cell = (nx, ny)
                if next_cell in visited:
                    continue
                visited.add(next_cell)
                came_from[next_cell] = ((x, y), _PATH_LETTERS[wall])
                queue.append(next_cell)
        else:
            raise ValueError("Exit is not reachable from entry.")

        steps: list[str] = []
        cell = exit_
        while cell != entry:
            cell, direction = came_from[cell]
            steps.append(direction)
        return "".join(reversed(steps))

    def _add_extra_passages(self, rng: random.Random) -> None:
        """Open a few extra passages without creating a 3-by-3 open area."""
        candidates: list[tuple[int, int, int, int, int]] = []
        for x, y in self._active_cells():
            for dx, dy, wall in ((1, 0, EAST), (0, 1, SOUTH)):
                nx, ny = x + dx, y + dy
                if self._is_active(nx, ny) and self.grid[y][x] & wall:
                    candidates.append((x, y, nx, ny, wall))
        rng.shuffle(candidates)
        active_count = self.width * self.height - len(self.blocked_cells)
        target = max(1, active_count // 10)
        opened = 0
        for x, y, nx, ny, wall in candidates:
            self._open_wall(x, y, nx, ny, wall)
            if self._has_open_3_by_3_area():
                self.grid[y][x] |= wall
                self.grid[ny][nx] |= OPPOSITE[wall]
                continue
            opened += 1
            if opened == target:
                return

    def _has_open_3_by_3_area(self) -> bool:
        """Return whether the grid contains a fully open 3-by-3 cell area."""
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                horizontal_open = all(
                    not self.grid[row][column] & EAST
                    for row in range(y, y + 3)
                    for column in range(x, x + 2)
                )
                vertical_open = all(
                    not self.grid[row][column] & SOUTH
                    for row in range(y, y + 2)
                    for column in range(x, x + 3)
                )
                if horizontal_open and vertical_open:
                    return True
        return False

    def _open_wall(self, x: int, y: int, nx: int, ny: int, wall: int) -> None:
        """Open the shared wall between two neighboring cells."""
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~OPPOSITE[wall]

    def _active_cells(self) -> Iterator[Coordinate]:
        """Yield all cells that are available to the generated maze."""
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in self.blocked_cells:
                    yield (x, y)

    def _is_active(self, x: int, y: int) -> bool:
        """Return whether a coordinate is in bounds and not blocked."""
        return self._in_bounds(x, y) and (x, y) not in self.blocked_cells

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return whether a coordinate belongs to this generator's grid."""
        return 0 <= x < self.width and 0 <= y < self.height
