"""GBFS decisions, tie handling, cycle safety and fixture validation."""

import unittest

from helpers import RouteAssertions, fixture_paths, load_case, reachable_states
from route_finding import parse_problem
from route_finding.algorithms.gbfs import gbfs
from route_finding.problem import RouteProblem


class GBFSTests(RouteAssertions, unittest.TestCase):
    def test_example(self):
        result = gbfs(load_case("test01_spec_example.txt"))
        self.assertEqual(result.goal.path(), [2, 3, 5])
        self.assertEqual(result.goal.path_cost, 10)
        self.assertEqual(result.nodes_created, 7)

    def test_greedy_can_choose_expensive_route(self):
        result = gbfs(load_case("test10_greedy_trap.txt"))
        self.assertEqual(result.goal.path(), [1, 2, 5])
        self.assertEqual(result.goal.path_cost, 34)  # Alternative costs only 18.

    def test_origin_is_goal(self):
        result = gbfs(RouteProblem({1: (0, 0)}, [], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_unreachable_cycle(self):
        problem = RouteProblem({i: (i, 0) for i in range(1, 4)},
                               [(1, 1, 0), (1, 2, 1), (2, 1, 1)], 1, {3})
        result = gbfs(problem)
        self.assertIsNone(result.goal)
        self.assertEqual(result.nodes_created, 4)

    def test_equal_sibling_priorities_use_ascending_ids(self):
        problem = RouteProblem({i: (0, 0) for i in range(1, 4)},
                               [(1, 3, 1), (1, 2, 1)], 1, {2, 3})
        self.assertEqual(gbfs(problem).goal.path(), [1, 2])

    def test_equal_priorities_across_branches_use_insertion_order(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3, 9]},
                               [(1, 2, 1), (1, 9, 1), (2, 3, 1)], 1, {3, 9})
        self.assertEqual(gbfs(problem).goal.path(), [1, 9])

    def test_all_fixtures_find_a_valid_route_when_one_exists(self):
        for case in fixture_paths():
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                result = gbfs(problem)
                if reachable_states(problem) & problem.destinations:
                    self.assertValidRoute(problem, result)
                else:
                    self.assertIsNone(result.goal)


if __name__ == "__main__":
    unittest.main()
