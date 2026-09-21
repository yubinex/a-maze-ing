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


def create_42_pattern(
    width: int,
    height: int,
    entry: Coordinate,
    exit_: Coordinate,
) -> set[Coordinate] | None:
    """Return centered closed cells that visibly form ``42``.

    Returns ``None`` when the maze cannot fit the pattern without covering an
    entry or exit cell.
    """
    pattern_width = len(_PATTERN[0])
    pattern_height = len(_PATTERN)
    if width < pattern_width or height < pattern_height:
        return None

    start_x = (width - pattern_width) // 2
    start_y = (height - pattern_height) // 2
    cells = {
        (start_x + x, start_y + y)
        for y, row in enumerate(_PATTERN)
        for x, value in enumerate(row)
        if value == "1"
    }
    if entry in cells or exit_ in cells:
        return None
    return cells
