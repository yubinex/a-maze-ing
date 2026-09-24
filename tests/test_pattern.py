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

    def test_moves_pattern_off_entry(self) -> None:
        cells = create_42_pattern(20, 15, (6, 5), (0, 0))
        self.assertNotIn((6, 5), cells)
        self.assertEqual(len(cells), 20)

    def test_moves_pattern_off_exit(self) -> None:
        cells = create_42_pattern(20, 15, (0, 0), (6, 5))
        self.assertNotIn((6, 5), cells)
        self.assertEqual(len(cells), 20)

    def test_moves_pattern_to_nearest_free_position(self) -> None:
        # Centre is (6, 5); moving one column right frees the entry.
        cells = create_42_pattern(20, 15, (6, 5), (19, 14))
        self.assertIn((7, 5), cells)

    def test_rejects_minimum_size_maze_with_entry_on_pattern(self) -> None:
        with self.assertRaisesRegex(PatternError, "no position"):
            create_42_pattern(7, 5, (0, 0), (6, 4))

    def test_rejects_pattern_that_splits_minimum_size_maze(self) -> None:
        with self.assertRaisesRegex(PatternError, "no position"):
            create_42_pattern(7, 5, (0, 3), (6, 3))

    def test_centers_pattern_and_returns_closed_cells(self) -> None:
        cells = create_42_pattern(20, 15, (0, 0), (19, 14))
        self.assertIn((6, 5), cells)
        self.assertIn((12, 9), cells)
        self.assertNotIn((0, 0), cells)
        self.assertEqual(len(cells), 20)
