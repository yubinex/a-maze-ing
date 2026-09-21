"""Tests for output formatting, CLI errors, and interactive error handling."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import call, patch

import a_maze_ing
from config import Config, ConfigError
from interactive import run_interactive
from output_writer import OutputError, format_maze, write_maze
from pattern import PatternError
from renderer import _path_cells, colorize, render_maze


class OutputWriterTests(unittest.TestCase):
    """Verify serialized maze content and filesystem error conversion."""

    def test_formats_grid_as_uppercase_hexadecimal_output(self) -> None:
        content = format_maze([[15, 10], [3, 0]], (0, 0), (1, 1), "ES")
        self.assertEqual(content, "FA\n30\n\n0,0\n1,1\nES\n")

    def test_writes_formatted_content_to_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "maze.txt"
            write_maze(str(destination), [[15]], (0, 0), (0, 0), "")
            self.assertEqual(
                destination.read_text(encoding="utf-8"), "F\n\n0,0\n0,0\n\n"
            )

    def test_wraps_write_failure_as_output_error(self) -> None:
        with self.assertRaisesRegex(OutputError, "cannot write file"):
            write_maze(
                "missing-directory/maze.txt", [[15]], (0, 0), (0, 0), ""
            )


class CommandLineTests(unittest.TestCase):
    """Verify main-program argument and setup error handling."""

    def test_rejects_missing_config_argument(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            status = a_maze_ing.main(["a_maze_ing.py"])
        self.assertEqual(status, 2)
        self.assertIn("Usage:", stderr.getvalue())

    @patch("a_maze_ing.load_config", side_effect=ConfigError("bad config"))
    def test_reports_config_error(self, _load_config: object) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            status = a_maze_ing.main(["a_maze_ing.py", "config.txt"])
        self.assertEqual(status, 1)
        self.assertIn("bad config", stderr.getvalue())

    def test_uses_empty_pattern_when_pattern_creation_fails(self) -> None:
        config = Config(8, 6, (0, 0), (7, 5), "maze.txt", True, None, "DFS")
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            with (
                patch("a_maze_ing.load_config", return_value=config),
                patch(
                    "a_maze_ing.create_42_pattern",
                    side_effect=PatternError("does not fit"),
                ),
                patch("a_maze_ing.run_interactive", return_value=0) as run,
            ):
                self.assertEqual(
                    a_maze_ing.main(["a_maze_ing.py", "config.txt"]), 0
                )
        self.assertEqual(run.call_args.args[1], set())


class RendererTests(unittest.TestCase):
    """Verify rendering helpers without writing to the terminal."""

    def test_colorize_wraps_text_with_color_and_reset(self) -> None:
        self.assertEqual(colorize("x", "<color>"), "<color>x\033[0m")

    def test_path_cells_follows_cardinal_directions(self) -> None:
        self.assertEqual(_path_cells((1, 1), "ESW"), {(2, 1), (2, 2), (1, 2)})

    def test_render_maze_prints_top_row_and_south_border(self) -> None:
        with patch("builtins.print") as printer:
            render_maze([[15]], entry=(0, 0), exit_=(0, 0))
        self.assertEqual(printer.call_count, 3)


class InteractiveErrorTests(unittest.TestCase):
    """Verify terminal failures and seed behavior in the session."""

    def test_returns_error_when_terminal_input_fails(self) -> None:
        config = Config(1, 1, (0, 0), (0, 0), "maze.txt", True, None, "DFS")
        with (
            patch("interactive._generate_maze", return_value=([[15]], "")),
            patch("interactive.render_maze"),
            patch("builtins.input", side_effect=OSError("terminal lost")),
            patch("builtins.print"),
        ):
            self.assertEqual(run_interactive(config, set()), 1)

    def test_quit_command_exits_interactive_session(self) -> None:
        config = Config(1, 1, (0, 0), (0, 0), "maze.txt", True, None, "DFS")
        with (
            patch("interactive._generate_maze", return_value=([[15]], "")),
            patch("interactive.render_maze"),
            patch("builtins.input", return_value="q"),
            patch("builtins.print"),
        ):
            self.assertEqual(run_interactive(config, set()), 0)

    def test_regenerate_reuses_configured_fixed_seed(self) -> None:
        config = Config(1, 1, (0, 0), (0, 0), "maze.txt", True, 42, "DFS")
        with (
            patch(
                "interactive._generate_maze", return_value=([[15]], "")
            ) as generate,
            patch("interactive.render_maze"),
            patch("builtins.input", side_effect=["r", "q"]),
            patch("builtins.print") as printer,
        ):
            self.assertEqual(run_interactive(config, set()), 0)
        self.assertEqual(
            generate.call_args_list,
            [call(config, set(), 42), call(config, set(), 42)],
        )
        printer.assert_any_call("Seed: 42 (fixed) | Perfect: True")
        printer.assert_any_call(
            "[r]egenerate (same maze: fixed seed)  [p]ath  [c]olor  [q]uit"
        )

    def test_regenerate_uses_new_random_seed_when_unconfigured(self) -> None:
        config = Config(1, 1, (0, 0), (0, 0), "maze.txt", True, None, "DFS")
        with (
            patch(
                "interactive._generate_maze", return_value=([[15]], "")
            ) as generate,
            patch("interactive.render_maze"),
            patch("interactive.random.randrange", side_effect=[11, 22]),
            patch("builtins.input", side_effect=["r", "q"]),
            patch("builtins.print") as printer,
        ):
            self.assertEqual(run_interactive(config, set()), 0)
        self.assertEqual(
            generate.call_args_list,
            [call(config, set(), 11), call(config, set(), 22)],
        )
        printer.assert_any_call("Seed: 11 (random) | Perfect: True")
        printer.assert_any_call(
            "[r]egenerate (new maze)  [p]ath  [c]olor  [q]uit"
        )
