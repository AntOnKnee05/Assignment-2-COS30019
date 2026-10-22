"""BFS: fewest moves, counting and route validity."""

import unittest

from helpers import RouteAssertions, fixture_paths, load_case, min_moves
from route_finding import parse_problem
from route_finding.algorithms.bfs import bfs
from route_finding.problem import RouteProblem


class BFSTests(RouteAssertions, unittest.TestCase):
    def test_counts_duplicate_child_in_example(self):
        result = bfs(load_case("test01_spec_example.txt"))
        self.assertEqual(result.goal.path(), [2, 1, 4])
        self.assertEqual(result.nodes_created, 5)

    def test_counts_rejected_self_loop(self):
        problem = RouteProblem({1: (0, 0), 2: (1, 0)}, [(1, 1, 0)], 1, {2})
        result = bfs(problem)
        self.assertIsNone(result.goal)
        self.assertEqual(result.nodes_created, 2)

    def test_origin_is_goal(self):
        result = bfs(RouteProblem({1: (0, 0)}, [], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_fewer_moves_even_when_more_expensive(self):
        result = bfs(load_case("test06_cheap_long_vs_short_expensive.txt"))
        self.assertEqual(result.goal.path(), [1, 5, 4])
        self.assertEqual(result.goal.path_cost, 40)

    def test_all_fixtures_minimize_moves(self):
        for case in fixture_paths():
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                optimum = min_moves(problem)
                result = bfs(problem)
                if optimum is None:
                    self.assertIsNone(result.goal)
                    continue
                self.assertValidRoute(problem, result)
                self.assertEqual(result.goal.depth, optimum)


if __name__ == "__main__":
    unittest.main()
