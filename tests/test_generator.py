"""Tests for reusable maze generation and shortest-path behavior."""

import unittest

from mazegen import EAST, NORTH, SOUTH, WEST, MazeGenerator


class MazeGeneratorTests(unittest.TestCase):
    """Verify generation inputs, maze invariants, and path solving."""

    def test_rejects_non_positive_dimensions(self) -> None:
        with self.assertRaisesRegex(ValueError, "positive"):
            MazeGenerator(0, 1)

    def test_rejects_out_of_bounds_blocked_cell(self) -> None:
        with self.assertRaisesRegex(ValueError, "inside"):
            MazeGenerator(2, 2, blocked_cells=[(2, 0)])

    def test_rejects_fully_blocked_maze(self) -> None:
        with self.assertRaisesRegex(ValueError, "At least one"):
            MazeGenerator(2, 2, blocked_cells=[(0, 0), (1, 0), (0, 1), (1, 1)])

    def test_seed_makes_generation_reproducible(self) -> None:
        first = MazeGenerator(8, 6, seed="repeatable").generate()
        second = MazeGenerator(8, 6, seed="repeatable").generate()
        self.assertEqual(first, second)

    def test_generated_maze_has_closed_outer_borders(self) -> None:
        maze = MazeGenerator(8, 6, seed=1).generate()
        self.assertTrue(all(cell & NORTH for cell in maze[0]))
        self.assertTrue(all(cell & SOUTH for cell in maze[-1]))
        self.assertTrue(all(row[0] & WEST for row in maze))
        self.assertTrue(all(row[-1] & EAST for row in maze))

    def test_neighboring_cells_have_matching_walls(self) -> None:
        maze = MazeGenerator(8, 6, seed=2).generate()
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                if x + 1 < len(row):
                    self.assertEqual(
                        bool(cell & EAST), bool(row[x + 1] & WEST)
                    )
                if y + 1 < len(maze):
                    self.assertEqual(
                        bool(cell & SOUTH), bool(maze[y + 1][x] & NORTH)
                    )

    def test_solution_path_is_available_after_generation(self) -> None:
        generator = MazeGenerator(8, 6, seed=3)
        generator.generate()
        path = generator.solution_path((0, 0), (7, 5))
        self.assertTrue(path)
        self.assertTrue(set(path) <= {"N", "E", "S", "W"})

    def test_solution_requires_generation(self) -> None:
        with self.assertRaisesRegex(ValueError, "Generate a maze"):
            MazeGenerator(2, 2).solution_path((0, 0), (1, 1))

    def test_solution_rejects_blocked_endpoint(self) -> None:
        generator = MazeGenerator(2, 2, blocked_cells=[(0, 0)])
        generator.generate()
        with self.assertRaisesRegex(ValueError, "non-blocked"):
            generator.solution_path((0, 0), (1, 1))

    def test_non_perfect_mazes_never_contain_open_3_by_3_area(self) -> None:
        for seed in range(10):
            generator = MazeGenerator(12, 10, seed=seed, perfect=False)
            generator.generate()
            self.assertFalse(generator._has_open_3_by_3_area())

    def test_rejects_disconnecting_blocked_cells(self) -> None:
        generator = MazeGenerator(
            3, 3, blocked_cells=[(1, 0), (1, 1), (1, 2)]
        )
        with self.assertRaisesRegex(ValueError, "divide the maze"):
            generator.generate()
