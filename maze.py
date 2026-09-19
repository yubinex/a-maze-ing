"""Compatibility API for existing maze generation callers."""

from mazegen import MazeGenerator


def generate_maze(
    width: int, height: int, seed: int | str | None = None
) -> list[list[int]]:
    """Generate a perfect maze through :class:`mazegen.MazeGenerator`.

    This small compatibility wrapper keeps existing callers working while new
    code should import and instantiate ``MazeGenerator`` directly.
    """
    return MazeGenerator(width, height, seed=seed).generate()
