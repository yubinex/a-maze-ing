# mazegen

Reusable grid-maze generation and shortest-path solving for Python 3.10+.
The package has no dependencies and exposes one class, `MazeGenerator`.

## Installation

```bash
python3 -m pip install mazegen-0.1.0-py3-none-any.whl
```

## Basic example

```python
from mazegen import MazeGenerator

generator = MazeGenerator(20, 15, seed=42)
grid = generator.generate()
path = generator.solution_path((0, 0), (19, 14))
print(path)  # e.g. "EESSEN..."
```

## Custom parameters

```python
MazeGenerator(
    width=30,               # number of columns (>= 1)
    height=20,              # number of rows (>= 1)
    seed=1234,              # int, str or None; same seed -> same maze
    perfect=False,          # True: exactly one path between any two cells
    blocked_cells={(5, 5)}, # (x, y) cells kept fully closed and unreachable
)
```

- `seed=None` produces a different maze on every call to `generate()`.
- `perfect=False` opens a few extra passages, creating loops, but never a
  fully open 3x3 area.
- Blocked cells must lie inside the maze and must not split the remaining
  cells into separate regions.

Invalid parameters raise `ValueError`.

## Accessing the generated structure

`generate()` returns the grid and also stores it in `generator.grid`. It is
a `list[list[int]]` indexed as `grid[y][x]`, where `(0, 0)` is the top-left
cell. Each value is a bitmask of the closed walls of that cell:

| Constant | Bit | Value |
|----------|-----|-------|
| `NORTH`  | 0   | 1     |
| `EAST`   | 1   | 2     |
| `SOUTH`  | 2   | 4     |
| `WEST`   | 3   | 8     |

```python
from mazegen import EAST, NORTH

cell = grid[0][0]
has_north_wall = bool(cell & NORTH)
has_east_wall = bool(cell & EAST)
```

Walls are always consistent between neighbours, and the outer border is
always closed.

## Accessing a solution

```python
path = generator.solution_path(entry=(0, 0), exit_=(19, 14))
```

Returns the shortest route as a string of `N`, `E`, `S` and `W` moves. It
raises `ValueError` if `generate()` has not been called, or if an endpoint
is outside the maze or blocked.
