"""A*: minimum cost against an independent Bellman-Ford reference."""

import unittest

from helpers import RouteAssertions, fixture_paths, load_case, min_cost
from route_finding import parse_problem
from route_finding.algorithms.astar import astar, heuristic_scale
from route_finding.problem import RouteProblem


class AStarTests(RouteAssertions, unittest.TestCase):
    def test_all_fixtures_have_optimal_cost(self):
        for case in fixture_paths():
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                optimum = min_cost(problem)
                result = astar(problem)
                if optimum is None:
                    self.assertIsNone(result.goal)
                    continue
                cost = self.assertValidRoute(problem, result)
                self.assertAlmostEqual(cost, optimum)

    def test_example(self):
        result = astar(load_case("test01_spec_example.txt"))
        self.assertEqual(result.goal.path(), [2, 3, 5])
        self.assertEqual(result.goal.path_cost, 10)
        self.assertEqual(result.nodes_created, 9)

    def test_goal_is_checked_on_removal(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 3, 10), (1, 2, 1), (2, 3, 1)], 1, {3})
        result = astar(problem)
        self.assertEqual(result.goal.path(), [1, 2, 3])
        self.assertEqual(result.goal.path_cost, 2)
        self.assertEqual(result.nodes_created, 4)

    def test_scaled_heuristic_repairs_overestimate(self):
        problem = load_case("test11_inadmissible_heuristic.txt")
        self.assertLess(heuristic_scale(problem), 1)
        self.assertEqual(astar(problem).goal.path_cost, 2)

    def test_scale_is_one_when_every_edge_is_at_least_its_length(self):
        self.assertEqual(heuristic_scale(load_case("test01_spec_example.txt")), 1)

    def test_zero_cost_cycle(self):
        problem = RouteProblem({i: (i, 0) for i in [1, 2, 3]},
                               [(1, 2, 0), (2, 1, 0), (2, 3, 0)], 1, {3})
        self.assertEqual(heuristic_scale(problem), 0)
        result = astar(problem)
        self.assertEqual(result.goal.path(), [1, 2, 3])
        self.assertEqual(result.goal.path_cost, 0)
        self.assertEqual(result.nodes_created, 4)

    def test_origin_goal(self):
        result = astar(RouteProblem({1: (0, 0)}, [], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_equal_priorities_preserve_sibling_order(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 3, 2), (1, 2, 2)], 1, {2, 3})
        self.assertEqual(astar(problem).goal.path(), [1, 2])

    def test_equal_priorities_across_branches_use_insertion_order(self):
        # Goals 3 (via 2) and 9 tie on f = 2; node 9 was added first.
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3, 9]},
                               [(1, 2, 1), (1, 9, 2), (2, 3, 1)], 1, {3, 9})
        self.assertEqual(astar(problem).goal.path(), [1, 9])


if __name__ == "__main__":
    unittest.main()
