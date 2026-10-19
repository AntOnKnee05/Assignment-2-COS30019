"""BFS counting regression tests."""
import unittest
from pathlib import Path
from route_finding import parse_problem
from route_finding.problem import RouteProblem
from route_finding.algorithms.bfs import bfs


class BFSTests(unittest.TestCase):
    def test_counts_duplicate_child_in_example(self):
        result = bfs(parse_problem(Path(__file__).parent / 'cases/test01_spec_example.txt'))
        self.assertEqual(result.goal.path(), [2, 1, 4])
        self.assertEqual(result.nodes_created, 5)

    def test_counts_rejected_self_loop(self):
        problem = RouteProblem({1: (0, 0), 2: (1, 0)}, [(1, 1, 0)], 1, {2})
        result = bfs(problem)
        self.assertIsNone(result.goal)
        self.assertEqual(result.nodes_created, 2)
