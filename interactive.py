"""Run the interactive terminal session for a generated maze."""

import random
import sys

from config import Config
from mazegen import Grid, MazeGenerator
from output_writer import OutputError, write_maze
from renderer import render_maze

Coordinate = tuple[int, int]
_WALL_COLORS = ("\033[37m", "\033[34m", "\033[33m", "\033[32m")
_SEED_RANGE = 2**63


def run_interactive(config: Config, pattern: set[Coordinate]) -> int:
    """Display a maze and process regeneration, path, color, and quit input.

    ``SEED`` seeds the whole session rather than one maze. Every maze draws
    its own seed from that session stream, so regenerating always builds a
    new maze while the sequence of mazes stays reproducible across runs.
    """
    fixed_seed = config.seed is not None
    session_seed = (
        config.seed if fixed_seed else random.randrange(_SEED_RANGE)
    )
    session_rng = random.Random(session_seed)
    maze_number = 1
    try:
        grid, path = _generate_maze(
            config, pattern, session_rng.randrange(_SEED_RANGE)
        )
    except (ValueError, OutputError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    show_path = True
    color_index = 0
    while True:
        if sys.stdout.isatty():
            print("\033[2J\033[H", end="")
        seed_kind = "fixed" if fixed_seed else "random"
        print(
            f"Seed: {session_seed!r} ({seed_kind}) | Maze {maze_number} "
            f"| Perfect: {config.perfect}"
        )
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
        except OSError as err:
            # A disconnected terminal or failed input stream should not crash
            # the interactive session with a traceback.
            print(f"Error: terminal input failed ({err})", file=sys.stderr)
            return 1
        if command == "q":
            return 0
        if command == "p":
            show_path = not show_path
        elif command == "c":
            color_index = (color_index + 1) % len(_WALL_COLORS)
        elif command == "r":
            try:
                grid, path = _generate_maze(
                    config, pattern, session_rng.randrange(_SEED_RANGE)
                )
                maze_number += 1
            except (ValueError, OutputError) as err:
                print(f"Error: {err}", file=sys.stderr)
                return 1
        elif command:
            print("Unknown command. Use r, p, c, or q.")


def _generate_maze(
    config: Config, blocked_cells: set[Coordinate], seed: int | str | None
) -> tuple[Grid, str]:
    """Generate one maze, write it to the output file, and return it.

    The returned path is expressed using the ``N``, ``E``, ``S``, and ``W``
    letters. Every generated maze replaces the previous output file, so the
    file always describes the maze currently on screen.
    """
    generator = MazeGenerator(
        config.width,
        config.height,
        seed=seed,
        perfect=config.perfect,
        blocked_cells=blocked_cells,
    )
    grid = generator.generate()
    path = generator.solution_path(config.entry, config.exit)
    write_maze(config.output_file, grid, config.entry, config.exit, path)
    return grid, path
