"""Colored ASCII rendering helpers for maze grids."""

from mazegen.constants import EAST, SOUTH

Coordinate = tuple[int, int]
_RESET = "\033[0m"
_WALL_COLOR = "\033[37m"
_ENTRY_COLOR = "\033[92m"
_EXIT_COLOR = "\033[91m"
_PATH_COLOR = "\033[96m"
_PATTERN_COLOR = "\033[95m"
_DELTAS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def colorize(text: str, color: str) -> str:
    """Return terminal text wrapped in an ANSI color and reset sequence."""
    return f"{color}{text}{_RESET}"


def print_top_border(width: int, wall_color: str) -> None:
    """Print the closed top border for a maze of the given width."""
    print(colorize("+" + "---+" * width, wall_color))


def print_cell_row(
    grid: list[list[int]],
    y: int,
    blocked_cells: set[Coordinate],
    entry: Coordinate,
    exit_: Coordinate,
    path_cells: set[Coordinate],
    wall_color: str,
) -> None:
    """Print one row of cell interiors and their east walls."""
    line = colorize("|", wall_color)
    for x in range(len(grid[y])):
        cell = (x, y)
        if cell == entry:
            line += colorize(" E ", _ENTRY_COLOR)
        elif cell == exit_:
            line += colorize(" X ", _EXIT_COLOR)
        elif cell in blocked_cells:
            line += colorize("###", _PATTERN_COLOR)
        elif cell in path_cells:
            line += colorize(" . ", _PATH_COLOR)
        else:
            line += "   "
        line += colorize("|" if grid[y][x] & EAST else " ", wall_color)
    print(line)


def print_south_border(grid: list[list[int]], y: int, wall_color: str) -> None:
    """Print the south walls below one row of cells."""
    line = "+"
    for x in range(len(grid[y])):
        line += "---+" if grid[y][x] & SOUTH else "   +"
    print(colorize(line, wall_color))


def render_maze(
    grid: list[list[int]],
    blocked_cells: set[Coordinate] | None = None,
    entry: Coordinate = (0, 0),
    exit_: Coordinate = (0, 0),
    path: str = "",
    wall_color: str = _WALL_COLOR,
) -> None:
    """Print walls, endpoints, blocked cells, and an optional solution path."""
    blocked = blocked_cells or set()
    path_cells = _path_cells(entry, path)
    print_top_border(len(grid[0]), wall_color)
    for y in range(len(grid)):
        print_cell_row(grid, y, blocked, entry, exit_, path_cells, wall_color)
        print_south_border(grid, y, wall_color)


def _path_cells(entry: Coordinate, path: str) -> set[Coordinate]:
    """Return every cell traversed by a path string, excluding its entry."""
    x, y = entry
    cells: set[Coordinate] = set()
    for direction in path:
        dx, dy = _DELTAS[direction]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells
