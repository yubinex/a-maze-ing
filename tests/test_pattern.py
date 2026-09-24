"""Tests for the closed-cell ``42`` pattern."""

import unittest

from pattern import PatternError, PatternTooSmallError, create_42_pattern


class PatternTests(unittest.TestCase):
    """Verify pattern placement and invalid-pattern handling."""

    def test_rejects_maze_narrower_than_pattern(self) -> None:
        with self.assertRaisesRegex(
            PatternTooSmallError, "needs at least 7x5"
        ):
            create_42_pattern(6, 5, (0, 0), (5, 4))

    def test_rejects_maze_shorter_than_pattern(self) -> None:
        with self.assertRaisesRegex(
            PatternTooSmallError, "needs at least 7x5"
        ):
            create_42_pattern(7, 4, (0, 0), (6, 3))

    def test_rejects_entry_covered_by_pattern(self) -> None:
        with self.assertRaisesRegex(PatternError, "cover ENTRY 6,5"):
            create_42_pattern(20, 15, (6, 5), (0, 0))

    def test_rejects_exit_covered_by_pattern(self) -> None:
        with self.assertRaisesRegex(PatternError, "cover EXIT 6,5"):
            create_42_pattern(20, 15, (0, 0), (6, 5))

    def test_rejects_pattern_that_splits_minimum_size_maze(self) -> None:
        with self.assertRaisesRegex(PatternError, "cut the maze"):
            create_42_pattern(7, 5, (0, 3), (6, 3))

    def test_centers_pattern_and_returns_closed_cells(self) -> None:
        cells = create_42_pattern(20, 15, (0, 0), (19, 14))
        self.assertIn((6, 5), cells)
        self.assertIn((12, 9), cells)
        self.assertNotIn((0, 0), cells)
        self.assertEqual(len(cells), 20)
