"""A-Maze-ing: generate a maze described by a configuration file.

Usage:
    python3 a_maze_ing.py config.txt
"""

import sys

from config import ConfigError, load_config
from interactive import run_interactive
from pattern import PatternError, PatternTooSmallError, create_42_pattern


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

    try:
        pattern = create_42_pattern(
            config.width, config.height, config.entry, config.exit
        )
    except PatternTooSmallError as err:
        print(f"Error: {err}; generating without it.", file=sys.stderr)
        pattern = set()
    except PatternError as err:
        print(f"Error: invalid 42 pattern: {err}", file=sys.stderr)
        return 1

    return run_interactive(config, pattern)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except BrokenPipeError:
        # A downstream command (for example, ``head``) may close a pipe early.
        # Treat that expected condition as a successful, quiet exit.
        sys.exit(0)
