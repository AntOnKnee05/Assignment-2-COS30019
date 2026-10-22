"""DFS behaviour and route validity checks."""

import unittest

from helpers import RouteAssertions, fixture_paths, load_case, reachable_states
from route_finding import parse_problem
from route_finding.algorithms.dfs import dfs
from route_finding.problem import RouteProblem


class DFSTests(RouteAssertions, unittest.TestCase):
    def test_example_route_and_created_count(self):
        result = dfs(load_case("test01_spec_example.txt"))
        self.assertEqual(result.goal.path(), [2, 1, 3, 5])
        self.assertEqual(result.goal.path_cost, 15)
        self.assertEqual(result.nodes_created, 9)

    def test_origin_is_goal(self):
        result = dfs(RouteProblem({1: (0, 0)}, [], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_unreachable_cycle_and_self_loop_terminate(self):
        problem = RouteProblem(
            {1: (0, 0), 2: (1, 0), 3: (2, 0)},
            [(1, 1, 0), (1, 2, 1), (2, 1, 1)], 1, {3})
        result = dfs(problem)
        self.assertIsNone(result.goal)
        self.assertEqual(result.nodes_created, 4)

    def test_deep_branch_before_shallow_goal(self):
        problem = RouteProblem(
            {i: (i, 0) for i in range(1, 5)},
            [(1, 4, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)], 1, {4})
        self.assertEqual(dfs(problem).goal.path(), [1, 2, 3, 4])

    def test_all_fixtures_find_a_valid_route_when_one_exists(self):
        for case in fixture_paths():
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                result = dfs(problem)
                if reachable_states(problem) & problem.destinations:
                    self.assertValidRoute(problem, result)
                else:
                    self.assertIsNone(result.goal)


if __name__ == "__main__":
    unittest.main()
