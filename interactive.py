"""Run the interactive terminal session for a generated maze."""

import random
import sys

from config import Config
from mazegen import Grid, MazeGenerator
from renderer import render_maze

Coordinate = tuple[int, int]
_WALL_COLORS = ("\033[37m", "\033[34m", "\033[33m", "\033[32m")


def run_interactive(config: Config, pattern: set[Coordinate]) -> int:
    """Display a maze and process regeneration, path, color, and quit input."""
    try:
        current_seed = config.seed
        grid, path = _generate_maze(config, pattern, current_seed)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    show_path = True
    color_index = 0
    while True:
        if sys.stdout.isatty():
            print("\033[2J\033[H", end="")
        print(f"Seed: {current_seed!r} | Perfect: {config.perfect}")
        render_maze(
            grid,
            pattern,
            config.entry,
            config.exit,
            path if show_path else "",
            _WALL_COLORS[color_index],
        )
        print("[r]egenerate  [p]ath  [c]olor  [q]uit")
        try:
            command = input("> ").strip().lower()
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.", file=sys.stderr)
            return 130
        if command == "q":
            return 0
        if command == "p":
            show_path = not show_path
        elif command == "c":
            color_index = (color_index + 1) % len(_WALL_COLORS)
        elif command == "r":
            try:
                current_seed = random.randrange(2**63)
                grid, path = _generate_maze(config, pattern, current_seed)
            except ValueError as err:
                print(f"Error: {err}", file=sys.stderr)
                return 1
        elif command:
            print("Unknown command. Use r, p, c, or q.")


def _generate_maze(
    config: Config, blocked_cells: set[Coordinate], seed: int | str | None
) -> tuple[Grid, str]:
    """Generate one maze and return its grid and shortest entry-to-exit path.

    The path is expressed using the ``N``, ``E``, ``S``, and ``W`` letters.
    """
    generator = MazeGenerator(
        config.width,
        config.height,
        seed=seed,
        perfect=config.perfect,
        blocked_cells=blocked_cells,
    )
    grid = generator.generate()
    return grid, generator.solution_path(config.entry, config.exit)
