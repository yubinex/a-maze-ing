"""Load and validate the A-Maze-ing configuration file.

The configuration file holds one ``KEY=VALUE`` pair per line. Blank lines
and lines starting with ``#`` are ignored.

Loading happens in three stages, each usable on its own:

1. ``load_config``  reads the file from disk.
2. ``parse_lines``  turns lines into raw strings, remembering line numbers.
3. ``build_config`` converts and validates those strings into a ``Config``.

Every problem is reported as a ``ConfigError`` whose message names the file
and, where possible, the line that caused it.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

MANDATORY_KEYS: Final[tuple[str, ...]] = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)
OPTIONAL_KEYS: Final[tuple[str, ...]] = ("SEED", "ALGORITHM")
SUPPORTED_ALGORITHMS: Final[tuple[str, ...]] = ("DFS",)
DEFAULT_ALGORITHM: Final[str] = "DFS"
MAX_DIMENSION: Final[int] = 1000
_DIGITS: Final[re.Pattern[str]] = re.compile(r"[0-9]+")

RawConfig = dict[str, tuple[str, int]]
"""Maps each key to its unconverted value and the line it was found on."""


class ConfigError(Exception):
    """Raised when the configuration cannot be read or is invalid."""


@dataclass(frozen=True)
class Config:
    """Validated maze configuration.

    Coordinates are ``(x, y)``: x is the column, y is the row, and ``(0, 0)``
    is the top-left cell.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: Entry cell as ``(x, y)``.
        exit: Exit cell as ``(x, y)``.
        output_file: Path the maze is written to.
        perfect: Whether exactly one path must link entry and exit.
        seed: Random seed, or ``None`` to pick one at random.
        algorithm: Name of the generation algorithm.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | str | None
    algorithm: str


def load_config(path: str) -> Config:
    """Read, parse and validate a configuration file.

    Args:
        path: Path to the configuration file.

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If the file cannot be read or its content is invalid.
    """
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except FileNotFoundError:
        raise ConfigError(f"{path}: file not found") from None
    except IsADirectoryError:
        raise ConfigError(f"{path}: is a directory, not a file") from None
    except PermissionError:
        raise ConfigError(f"{path}: permission denied") from None
    except UnicodeDecodeError:
        raise ConfigError(f"{path}: not a UTF-8 text file") from None
    except OSError as err:
        raise ConfigError(f"{path}: cannot read file ({err})") from None

    config = build_config(parse_lines(lines, path), path)
    if Path(config.output_file).resolve() == Path(path).resolve():
        raise ConfigError(
            f"{path}: OUTPUT_FILE must not overwrite the configuration file"
        )
    return config


def parse_lines(lines: Iterable[str], source: str) -> RawConfig:
    """Split configuration lines into raw key/value pairs.

    Values are not converted here; only the ``KEY=VALUE`` syntax is checked.

    Args:
        lines: Lines of the configuration file, without line endings.
        source: Name used in error messages (usually the file path).

    Returns:
        Each key mapped to its stripped value and its 1-based line number.

    Raises:
        ConfigError: On a malformed line, an unknown key or a duplicate key.
    """
    known_keys = MANDATORY_KEYS + OPTIONAL_KEYS
    raw: RawConfig = {}
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            raise ConfigError(
                f"{source}:{number}: expected KEY=VALUE, got '{stripped}'"
            )
        key, value = stripped.split("=", 1)
        key = key.strip().upper()
        if not key:
            raise ConfigError(f"{source}:{number}: missing key before '='")
        if key not in known_keys:
            raise ConfigError(
                f"{source}:{number}: unknown key '{key}' "
                f"(known keys: {', '.join(known_keys)})"
            )
        if key in raw:
            first_line = raw[key][1]
            raise ConfigError(
                f"{source}:{number}: duplicate key '{key}' "
                f"(first defined on line {first_line})"
            )
        raw[key] = (value.strip(), number)
    return raw


def build_config(raw: RawConfig, source: str) -> Config:
    """Convert raw key/value pairs into a validated ``Config``.

    Args:
        raw: Output of ``parse_lines``.
        source: Name used in error messages (usually the file path).

    Returns:
        The validated configuration.

    Raises:
        ConfigError: If a key is missing or a value is invalid.
    """
    missing = [key for key in MANDATORY_KEYS if key not in raw]
    if missing:
        raise ConfigError(
            f"{source}: missing mandatory key(s): {', '.join(missing)}"
        )

    def where(key: str) -> str:
        """Return ``source:line`` for the line that defined ``key``."""
        return f"{source}:{raw[key][1]}"

    width = _parse_dimension(raw["WIDTH"][0], "WIDTH", where("WIDTH"))
    height = _parse_dimension(raw["HEIGHT"][0], "HEIGHT", where("HEIGHT"))
    entry = _parse_coordinates(raw["ENTRY"][0], "ENTRY", where("ENTRY"))
    exit_ = _parse_coordinates(raw["EXIT"][0], "EXIT", where("EXIT"))
    for key, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if x >= width or y >= height:
            raise ConfigError(
                f"{where(key)}: {key} {x},{y} is outside the maze "
                f"(x must be < {width}, y must be < {height})"
            )
    if entry == exit_:
        raise ConfigError(
            f"{where('EXIT')}: EXIT must differ from ENTRY "
            f"({entry[0]},{entry[1]})"
        )

    output_file = raw["OUTPUT_FILE"][0]
    if not output_file:
        raise ConfigError(f"{where('OUTPUT_FILE')}: OUTPUT_FILE is empty")

    perfect = _parse_bool(raw["PERFECT"][0], "PERFECT", where("PERFECT"))

    seed: int | str | None = None
    if "SEED" in raw and raw["SEED"][0]:
        seed_text = raw["SEED"][0]
        seed = int(seed_text) if _DIGITS.fullmatch(seed_text) else seed_text

    algorithm = DEFAULT_ALGORITHM
    if "ALGORITHM" in raw:
        algorithm = raw["ALGORITHM"][0].upper()
        if algorithm not in SUPPORTED_ALGORITHMS:
            raise ConfigError(
                f"{where('ALGORITHM')}: unsupported ALGORITHM "
                f"'{raw['ALGORITHM'][0]}' "
                f"(supported: {', '.join(SUPPORTED_ALGORITHMS)})"
            )

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm,
    )


def _parse_int(value: str, key: str, where: str) -> int:
    """Parse a non-negative integer written with ASCII digits only.

    ``int()`` alone is too lenient: it accepts ``+5``, ``-5`` and ``1_000``.
    """
    if not _DIGITS.fullmatch(value):
        raise ConfigError(
            f"{where}: {key} must be a non-negative integer, got '{value}'"
        )
    return int(value)


def _parse_dimension(value: str, key: str, where: str) -> int:
    """Parse a maze dimension between 1 and ``MAX_DIMENSION``."""
    number = _parse_int(value, key, where)
    if not 1 <= number <= MAX_DIMENSION:
        raise ConfigError(
            f"{where}: {key} must be between 1 and {MAX_DIMENSION}, "
            f"got {number}"
        )
    return number


def _parse_coordinates(value: str, key: str, where: str) -> tuple[int, int]:
    """Parse ``x,y`` into a tuple of two non-negative integers."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{where}: {key} must be 'x,y', got '{value}'")
    x = _parse_int(parts[0].strip(), f"{key} x", where)
    y = _parse_int(parts[1].strip(), f"{key} y", where)
    return (x, y)


def _parse_bool(value: str, key: str, where: str) -> bool:
    """Parse ``True`` or ``False``, ignoring case."""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise ConfigError(f"{where}: {key} must be True or False, got '{value}'")
