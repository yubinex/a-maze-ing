"""Write generated mazes in the output file format of the subject.

The file holds one hexadecimal digit per cell, one row per line. A digit has
one bit per closed wall: North is bit 0, East bit 1, South bit 2 and West
bit 3. After an empty line, three lines follow: the entry coordinates, the
exit coordinates and the shortest path from entry to exit.
"""

from mazegen import Grid

Coordinate = tuple[int, int]


class OutputError(Exception):
    """Raised when the maze cannot be written to its output file."""


def format_maze(
    grid: Grid,
    entry: Coordinate,
    exit_: Coordinate,
    solution: str,
) -> str:
    """Return the complete output file content for one generated maze.

    Args:
        grid: Wall bitmasks of the generated maze, indexed as ``grid[y][x]``.
        entry: Entry cell as ``(x, y)``.
        exit_: Exit cell as ``(x, y)``.
        solution: Shortest entry-to-exit path as ``N``/``E``/``S``/``W``.

    Returns:
        The file content, with every line terminated by ``\\n``.
    """
    rows = "".join(
        "".join(format(cell, "X") for cell in row) + "\n" for row in grid
    )
    return (
        f"{rows}"
        "\n"
        f"{entry[0]},{entry[1]}\n"
        f"{exit_[0]},{exit_[1]}\n"
        f"{solution}\n"
    )


def write_maze(
    destination: str,
    grid: Grid,
    entry: Coordinate,
    exit_: Coordinate,
    solution: str,
) -> None:
    """Write one generated maze to ``destination``, replacing that file.

    Args:
        destination: Path taken from the ``OUTPUT_FILE`` configuration key.
        grid: Wall bitmasks of the generated maze.
        entry: Entry cell as ``(x, y)``.
        exit_: Exit cell as ``(x, y)``.
        solution: Shortest entry-to-exit path as ``N``/``E``/``S``/``W``.

    Raises:
        OutputError: If the file cannot be written.
    """
    content = format_maze(grid, entry, exit_, solution)
    try:
        with open(destination, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as err:
        raise OutputError(
            f"{destination}: cannot write file ({err})"
        ) from None
