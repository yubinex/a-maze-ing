"""ASCII rendering helpers for maze grids."""

from mazegen.constants import EAST, SOUTH


def print_top_border(width: int) -> None:
    """Print the closed top border for a maze of the given width."""
    print("+" + "---+" * width)


def print_cell_row(grid: list[list[int]], y: int) -> None:
    """Print one row of cell interiors and their east walls."""
    line = "|"
    for x in range(len(grid[y])):
        line += "   "
        line += "|" if grid[y][x] & EAST else " "
    print(line)


def print_south_border(grid: list[list[int]], y: int) -> None:
    """Print the south walls below one row of cells."""
    line = "+"
    for x in range(len(grid[y])):
        line += "---+" if grid[y][x] & SOUTH else "   +"
    print(line)


def render_maze(grid: list[list[int]]) -> None:
    """Print the complete ASCII representation of a maze grid."""
    print_top_border(len(grid[0]))
    for y in range(len(grid)):
        print_cell_row(grid, y)
        print_south_border(grid, y)
