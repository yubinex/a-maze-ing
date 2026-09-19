"""A-Maze-ing: generate a maze described by a configuration file.

Usage:
    python3 a_maze_ing.py config.txt
"""

import sys

from config import ConfigError, load_config
from interactive import run_interactive
from pattern import create_42_pattern


def main(argv: list[str]) -> int:
    """Run the program.

    Args:
        argv: Command-line arguments, including the program name.

    Returns:
        The process exit status: 0 on success, non-zero on error.
    """
    if len(argv) != 2:
        print(f"Usage: python3 {argv[0]} <config_file>", file=sys.stderr)
        return 2
    try:
        config = load_config(argv[1])
    except ConfigError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    pattern = create_42_pattern(
        config.width, config.height, config.entry, config.exit
    )
    if pattern is None:
        print(
            "Error: Maze is too small to display the 42 pattern.",
            file=sys.stderr,
        )
        pattern = set()

    return run_interactive(config, pattern)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
