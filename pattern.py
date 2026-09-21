"""Build the closed-cell ``42`` pattern used by the application."""

from typing import Final

Coordinate = tuple[int, int]

_PATTERN: Final[tuple[str, ...]] = (
    "1010111",
    "1010001",
    "1110111",
    "0010100",
    "0010111",
)


class PatternError(Exception):
    """Raised when the ``42`` pattern does not fit the configured maze."""


def create_42_pattern(
    width: int,
    height: int,
    entry: Coordinate,
    exit_: Coordinate,
) -> set[Coordinate]:
    """Return centered closed cells that visibly form ``42``.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell as ``(x, y)``.
        exit_: Exit cell as ``(x, y)``.

    Returns:
        The cells that the pattern keeps fully closed.

    Raises:
        PatternError: If the maze is too small for the pattern, if the pattern
            would cover the entry or the exit, or if it would cut the maze
            into regions that cannot reach each other.
    """
    pattern_width = len(_PATTERN[0])
    pattern_height = len(_PATTERN)
    if width < pattern_width or height < pattern_height:
        raise PatternError(
            f"maze is too small for the 42 pattern (needs at least "
            f"{pattern_width}x{pattern_height}, got {width}x{height})"
        )

    start_x = (width - pattern_width) // 2
    start_y = (height - pattern_height) // 2
    cells = {
        (start_x + x, start_y + y)
        for y, row in enumerate(_PATTERN)
        for x, value in enumerate(row)
        if value == "1"
    }
    for key, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if (x, y) in cells:
            raise PatternError(
                f"the 42 pattern would cover {key} {x},{y}"
            )
    if _splits_maze(width, height, cells, entry):
        raise PatternError(
            "the 42 pattern would cut the maze into regions that cannot "
            "reach each other"
        )
    return cells


def _splits_maze(
    width: int,
    height: int,
    cells: set[Coordinate],
    start: Coordinate,
) -> bool:
    """Return whether closing ``cells`` leaves an open cell unreachable.

    The generator needs every non-closed cell to be reachable from every
    other one, so the pattern is only usable when a flood fill from ``start``
    covers all of them.
    """
    reached: set[Coordinate] = {start}
    stack: list[Coordinate] = [start]
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)):
            if not (0 <= nx < width and 0 <= ny < height):
                continue
            if (nx, ny) in cells or (nx, ny) in reached:
                continue
            reached.add((nx, ny))
            stack.append((nx, ny))
    return len(reached) != width * height - len(cells)
