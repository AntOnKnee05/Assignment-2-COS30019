"""Compare A* against independent Bellman-Ford shortest-path costs."""

from pathlib import Path
import unittest

from route_finding import parse_problem
from route_finding.problem import RouteProblem
from route_finding.algorithms.astar import astar, heuristic_scale


class AStarTests(unittest.TestCase):
    def test_all_fifteen_cases_have_optimal_cost(self):
        cases = sorted((Path(__file__).parent / 'cases').glob('test*.txt'))
        self.assertGreaterEqual(len(cases), 15)
        for case in cases:
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                distances = dict.fromkeys(problem.nodes, float('inf'))
                distances[problem.origin] = 0
                for _ in range(len(problem.nodes) - 1):
                    for source in problem.nodes:
                        for target, cost in problem.successors(source):
                            distances[target] = min(distances[target],
                                                    distances[source] + cost)
                optimum = min(distances[g] for g in problem.destinations)
                result = astar(problem)
                if optimum == float('inf'):
                    self.assertIsNone(result.goal)
                    continue
                self.assertIsNotNone(result.goal)
                self.assertAlmostEqual(result.goal.path_cost, optimum)
                path = result.goal.path()
                self.assertEqual(path[0], problem.origin)
                self.assertIn(path[-1], problem.destinations)
                self.assertEqual(len(path), len(set(path)))
                total = 0
                for source, target in zip(path, path[1:]):
                    edges = dict(problem.successors(source))
                    self.assertIn(target, edges)
                    total += edges[target]
                self.assertAlmostEqual(total, optimum)

    def test_goal_is_checked_on_removal(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 3, 10), (1, 2, 1), (2, 3, 1)], 1, {3})
        result = astar(problem)
        self.assertEqual(result.goal.path(), [1, 2, 3])
        self.assertEqual(result.goal.path_cost, 2)
        self.assertEqual(result.nodes_created, 4)

    def test_scaled_heuristic_repairs_overestimate(self):
        problem = parse_problem(Path(__file__).parent / 'cases/test11_inadmissible_heuristic.txt')
        self.assertLess(heuristic_scale(problem), 1)
        self.assertEqual(astar(problem).goal.path_cost, 2)

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


if __name__ == '__main__':
    unittest.main()
