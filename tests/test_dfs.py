"""DFS behaviour and route validity checks, using the standard library."""

from pathlib import Path
import unittest

from route_finding import parse_problem
from route_finding.problem import RouteProblem
from route_finding.algorithms.dfs import dfs


class DFSTests(unittest.TestCase):
    def test_example_route_and_created_count(self):
        problem = parse_problem(Path(__file__).parent / 'cases/test01_spec_example.txt')
        result = dfs(problem)
        self.assertEqual(result.goal.path(), [2, 1, 3, 5])
        self.assertEqual(result.goal.path_cost, 15)
        self.assertEqual(result.nodes_created, 9)

    def test_origin_is_goal(self):
        problem = RouteProblem({1: (0, 0)}, [], 1, {1})
        result = dfs(problem)
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

    def test_all_fifteen_fixtures(self):
        cases = sorted((Path(__file__).parent / 'cases').glob('test*.txt'))
        self.assertGreaterEqual(len(cases), 15)
        for case in cases:
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                # Independent reachability check, without search-tree nodes.
                reachable = {problem.origin}
                pending = [problem.origin]
                while pending:
                    for state, _ in problem.successors(pending.pop()):
                        if state not in reachable:
                            reachable.add(state)
                            pending.append(state)
                result = dfs(problem)
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
