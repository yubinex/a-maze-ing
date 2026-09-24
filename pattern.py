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
    """Raised when the ``42`` pattern cannot be used in a maze."""


class PatternTooSmallError(PatternError):
    """Raised when a maze is too small to contain the ``42`` pattern."""


def create_42_pattern(
    width: int,
    height: int,
    entry: Coordinate,
    exit_: Coordinate,
) -> set[Coordinate]:
    """Return closed cells that visibly form ``42``, as centred as possible.

    The centred position is preferred. If it would cover the entry or the
    exit, or cut the maze into unreachable regions, the nearest position that
    does neither is used instead.

    Args:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell as ``(x, y)``.
        exit_: Exit cell as ``(x, y)``.

    Returns:
        The cells that the pattern keeps fully closed.

    Raises:
        PatternTooSmallError: If the maze is smaller than the pattern.
        PatternError: If no position keeps the entry and exit free and every
            open cell reachable.
    """
    pattern_width = len(_PATTERN[0])
    pattern_height = len(_PATTERN)
    if width < pattern_width or height < pattern_height:
        raise PatternTooSmallError(
            f"maze is too small for the 42 pattern (needs at least "
            f"{pattern_width}x{pattern_height}, got {width}x{height})"
        )

    center_x = (width - pattern_width) // 2
    center_y = (height - pattern_height) // 2
    starts = sorted(
        (
            (start_x, start_y)
            for start_y in range(height - pattern_height + 1)
            for start_x in range(width - pattern_width + 1)
        ),
        key=lambda start: (
            abs(start[0] - center_x) + abs(start[1] - center_y)
        ),
    )
    for start_x, start_y in starts:
        cells = {
            (start_x + x, start_y + y)
            for y, row in enumerate(_PATTERN)
            for x, value in enumerate(row)
            if value == "1"
        }
        if entry in cells or exit_ in cells:
            continue
        if not _splits_maze(width, height, cells, entry):
            return cells
    raise PatternError(
        "no position for the 42 pattern keeps ENTRY and EXIT free and "
        "every cell reachable"
    )


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
