"""Tests for configuration parsing and validation."""

import tempfile
import unittest
from pathlib import Path

from config import Config, ConfigError, build_config, load_config, parse_lines


def _valid_lines() -> list[str]:
    """Return a minimal valid configuration."""
    return [
        "WIDTH=8",
        "HEIGHT=6",
        "ENTRY=0,0",
        "EXIT=7,5",
        "OUTPUT_FILE=maze.txt",
        "PERFECT=True",
    ]


class ParseLinesTests(unittest.TestCase):
    """Verify syntax-level configuration parsing."""

    def test_ignores_blank_lines_and_comments(self) -> None:
        raw = parse_lines(["", " # comment", "WIDTH = 8"], "config")
        self.assertEqual(raw, {"WIDTH": ("8", 3)})

    def test_normalizes_keys(self) -> None:
        raw = parse_lines(["width=8"], "config")
        self.assertIn("WIDTH", raw)

    def test_rejects_missing_equals_sign(self) -> None:
        with self.assertRaisesRegex(ConfigError, "expected KEY=VALUE"):
            parse_lines(["WIDTH 8"], "config")

    def test_rejects_unknown_key(self) -> None:
        with self.assertRaisesRegex(ConfigError, "unknown key"):
            parse_lines(["UNKNOWN=value"], "config")

    def test_rejects_duplicate_key(self) -> None:
        with self.assertRaisesRegex(ConfigError, "duplicate key"):
            parse_lines(["WIDTH=8", "WIDTH=9"], "config")


class BuildConfigTests(unittest.TestCase):
    """Verify conversion from parsed values to ``Config``."""

    def test_builds_full_configuration_with_optional_values(self) -> None:
        raw = parse_lines(
            _valid_lines() + ["SEED=42", "ALGORITHM=dfs"], "config"
        )
        config = build_config(raw, "config")
        self.assertEqual(
            config,
            Config(8, 6, (0, 0), (7, 5), "maze.txt", True, 42, "DFS"),
        )

    def test_keeps_non_numeric_seed_as_text(self) -> None:
        raw = parse_lines(_valid_lines() + ["SEED=reproducible"], "config")
        self.assertEqual(build_config(raw, "config").seed, "reproducible")

    def test_requires_all_mandatory_keys(self) -> None:
        raw = parse_lines(_valid_lines()[1:], "config")
        with self.assertRaisesRegex(ConfigError, "missing mandatory key"):
            build_config(raw, "config")

    def test_rejects_out_of_bounds_endpoint(self) -> None:
        lines = _valid_lines()
        lines[3] = "EXIT=8,5"
        with self.assertRaisesRegex(ConfigError, "outside the maze"):
            build_config(parse_lines(lines, "config"), "config")

    def test_rejects_identical_endpoints(self) -> None:
        lines = _valid_lines()
        lines[3] = "EXIT=0,0"
        with self.assertRaisesRegex(ConfigError, "must differ"):
            build_config(parse_lines(lines, "config"), "config")

    def test_rejects_invalid_boolean(self) -> None:
        lines = _valid_lines()
        lines[-1] = "PERFECT=yes"
        with self.assertRaisesRegex(ConfigError, "must be True or False"):
            build_config(parse_lines(lines, "config"), "config")

    def test_rejects_unsupported_algorithm(self) -> None:
        lines = _valid_lines() + ["ALGORITHM=PRIM"]
        with self.assertRaisesRegex(ConfigError, "unsupported ALGORITHM"):
            build_config(parse_lines(lines, "config"), "config")


class LoadConfigTests(unittest.TestCase):
    """Verify filesystem errors and path-level validation."""

    def test_reports_missing_file(self) -> None:
        with self.assertRaisesRegex(ConfigError, "file not found"):
            load_config("missing-config-file.txt")

    def test_rejects_output_overwriting_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.txt"
            path.write_text("\n".join(_valid_lines()[:-2] + [
                f"OUTPUT_FILE={path}", "PERFECT=True",
            ]), encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "must not overwrite"):
                load_config(str(path))
