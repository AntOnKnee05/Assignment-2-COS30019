"""CUS1 (IDDFS): fewest moves, checked against an independent reference."""

import unittest

from helpers import RouteAssertions, fixture_paths, load_case, min_moves
from route_finding import parse_problem
from route_finding.algorithms.cus1 import cus1
from route_finding.problem import RouteProblem


class IDDFSTests(RouteAssertions, unittest.TestCase):
    def test_all_fixtures_minimize_moves(self):
        for case in fixture_paths():
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                optimum = min_moves(problem)
                result = cus1(problem)
                if optimum is None:
                    self.assertIsNone(result.goal)
                    continue
                self.assertValidRoute(problem, result)
                self.assertEqual(result.goal.depth, optimum)

    def test_example(self):
        result = cus1(load_case("test01_spec_example.txt"))
        self.assertEqual(result.goal.path(), [2, 1, 4])
        self.assertEqual(result.nodes_created, 8)

    def test_fewer_moves_even_when_more_expensive(self):
        result = cus1(load_case("test06_cheap_long_vs_short_expensive.txt"))
        self.assertEqual(result.goal.path(), [1, 5, 4])
        self.assertEqual(result.goal.depth, 2)
        self.assertEqual(result.goal.path_cost, 40)

    def test_origin_goal_without_edges(self):
        result = cus1(RouteProblem({1: (0, 0)}, [], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_no_edges_unreachable(self):
        result = cus1(RouteProblem({1: (0, 0), 2: (1, 0)}, [], 1, {2}))
        self.assertIsNone(result.goal)
        self.assertEqual(result.nodes_created, 1)

    def test_coincident_coordinates_and_cycle(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 2, 1), (2, 1, 1), (2, 3, 1)], 1, {3})
        result = cus1(problem)
        self.assertEqual(result.goal.path(), [1, 2, 3])
        self.assertEqual(result.nodes_created, 7)

    def test_equal_priorities_use_sibling_order(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 3, 1), (1, 2, 9)], 1, {2, 3})
        self.assertEqual(cus1(problem).goal.path(), [1, 2])


if __name__ == "__main__":
    unittest.main()
