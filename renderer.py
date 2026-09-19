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


def print_top_border(width: int) -> None:
    """Print the closed top border for a maze of the given width."""
    print(f"{_WALL_COLOR}+{'---+' * width}{_RESET}")


def print_cell_row(
    grid: list[list[int]],
    y: int,
    blocked_cells: set[Coordinate],
    entry: Coordinate,
    exit_: Coordinate,
    path_cells: set[Coordinate],
) -> None:
    """Print one row of cell interiors and their east walls."""
    line = f"{_WALL_COLOR}|"
    for x in range(len(grid[y])):
        cell = (x, y)
        if cell == entry:
            line += f"{_ENTRY_COLOR} E {_WALL_COLOR}"
        elif cell == exit_:
            line += f"{_EXIT_COLOR} X {_WALL_COLOR}"
        elif cell in blocked_cells:
            line += f"{_PATTERN_COLOR}###{_WALL_COLOR}"
        elif cell in path_cells:
            line += f"{_PATH_COLOR} . {_WALL_COLOR}"
        else:
            line += "   "
        line += "|" if grid[y][x] & EAST else " "
    print(f"{line}{_RESET}")


def print_south_border(grid: list[list[int]], y: int) -> None:
    """Print the south walls below one row of cells."""
    line = "+"
    for x in range(len(grid[y])):
        line += "---+" if grid[y][x] & SOUTH else "   +"
    print(f"{_WALL_COLOR}{line}{_RESET}")


def render_maze(
    grid: list[list[int]],
    blocked_cells: set[Coordinate] | None = None,
    entry: Coordinate = (0, 0),
    exit_: Coordinate = (0, 0),
    path: str = "",
) -> None:
    """Print walls, endpoints, blocked cells, and an optional solution path."""
    blocked = blocked_cells or set()
    path_cells = _path_cells(entry, path)
    print_top_border(len(grid[0]))
    for y in range(len(grid)):
        print_cell_row(grid, y, blocked, entry, exit_, path_cells)
        print_south_border(grid, y)


def _path_cells(entry: Coordinate, path: str) -> set[Coordinate]:
    """Return every cell traversed by a path string, excluding its entry."""
    x, y = entry
    cells: set[Coordinate] = set()
    for direction in path:
        dx, dy = _DELTAS[direction]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells
