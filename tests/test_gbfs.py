"""GBFS decisions, tie handling, cycle safety, and fixture validation."""

from pathlib import Path
import unittest

from route_finding import parse_problem
from route_finding.problem import RouteProblem
from route_finding.algorithms.gbfs import gbfs


class GBFSTests(unittest.TestCase):
    def test_example(self):
        problem = parse_problem(Path(__file__).parent / 'cases/test01_spec_example.txt')
        result = gbfs(problem)
        self.assertEqual(result.goal.path(), [2, 3, 5])
        self.assertEqual(result.goal.path_cost, 10)
        self.assertEqual(result.nodes_created, 7)

    def test_greedy_can_choose_expensive_route(self):
        problem = parse_problem(Path(__file__).parent / 'cases/test10_greedy_trap.txt')
        result = gbfs(problem)
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

    def test_all_fifteen_fixtures(self):
        cases = sorted((Path(__file__).parent / 'cases').glob('test*.txt'))
        self.assertGreaterEqual(len(cases), 15)
        for case in cases:
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                reachable = {problem.origin}
                pending = [problem.origin]
                while pending:
                    for state, _ in problem.successors(pending.pop()):
                        if state not in reachable:
                            reachable.add(state)
                            pending.append(state)
                result = gbfs(problem)
                self.assertEqual(result.goal is not None,
                                 bool(reachable & problem.destinations))
                if result.goal is None:
                    continue
                path = result.goal.path()
                self.assertEqual(path[0], problem.origin)
                self.assertIn(path[-1], problem.destinations)
                self.assertEqual(len(path), len(set(path)))
                cost = 0
                for source, target in zip(path, path[1:]):
                    edges = dict(problem.successors(source))
                    self.assertIn(target, edges)
                    cost += edges[target]
                self.assertAlmostEqual(result.goal.path_cost, cost)


if __name__ == '__main__':
    unittest.main()
