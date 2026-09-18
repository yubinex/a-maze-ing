import random


N = 1
E = 2
S = 4
W = 8
ALL_WALLS = N | E | S | W

# Each item contains dx, dy, this cell's wall, and the neighbour's wall.
DIRECTIONS = ((0, -1, N, S), (1, 0, E, W), (0, 1, S, N), (-1, 0, W, E))


def make_grid(width: int, height: int) -> list[list[int]]:
    """Create a height-by-width grid with every wall initially closed."""
    return [[ALL_WALLS for _ in range(width)] for _ in range(height)]


def generate_maze(width: int, height: int, seed: int | None = None) -> list[list[int]]:
    """Generate a connected perfect maze with randomized depth-first search."""
    if width < 1 or height < 1:
        raise ValueError("Maze dimensions must be positive.")

    grid = make_grid(width, height)
    rng = random.Random(seed)
    visited = {(0, 0)}
    stack = [(0, 0)]

    while stack:
        x, y = stack[-1]
        choices = []
        for dx, dy, wall, opposite in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                choices.append((nx, ny, wall, opposite))

        if not choices:
            stack.pop()
            continue

        nx, ny, wall, opposite = rng.choice(choices)
        grid[y][x] &= ~wall
        grid[ny][nx] &= ~opposite
        visited.add((nx, ny))
        stack.append((nx, ny))

    return grid


def open_east(grid: list[list[int]], x: int, y: int) -> None:
    """Open the passage between a cell and its eastern neighbour."""
    grid[y][x] &= ~E
    grid[y][x + 1] &= ~W


def open_south(grid: list[list[int]], x: int, y: int) -> None:
    """Open the passage between a cell and its southern neighbour."""
    grid[y][x] &= ~S
    grid[y + 1][x] &= ~N


def print_top_border(width: int) -> None:
    """Print the closed top border for a maze of the given width."""
    print("+" + "---+" * width)


def print_cell_row(grid: list[list[int]], y: int) -> None:
    """Print one row of cell interiors and their east walls."""
    line = "|"
    for x in range(len(grid[y])):
        line += "   "
        if grid[y][x] & E:
            line += "|"
        else:
            line += " "
    print(line)


def print_south_border(grid: list[list[int]], y: int) -> None:
    """Print the south walls below one row of cells."""
    line = "+"
    for x in range(len(grid[y])):
        if grid[y][x] & S:
            line += "---+"
        else:
            line += "   +"
    print(line)


def render_maze(grid: list[list[int]]) -> None:
    """Print the complete ASCII representation of a maze grid."""
    print_top_border(len(grid[0]))
    for y in range(len(grid)):
        print_cell_row(grid, y)
        print_south_border(grid, y)


# Example usage:
# grid = generate_maze(10, 6, seed=42)
# render_maze(grid)
