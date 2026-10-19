"""CUS2 minimum-move checks independent of the repository BFS method."""

from collections import deque
from pathlib import Path
import unittest

from route_finding import parse_problem
from route_finding.problem import RouteProblem
from route_finding.algorithms.cus2 import cus2


class CUS2Tests(unittest.TestCase):
    def test_all_fifteen_fixtures_minimize_moves(self):
        cases = sorted((Path(__file__).parent / 'cases').glob('test*.txt'))
        self.assertGreaterEqual(len(cases), 15)
        for case in cases:
            with self.subTest(case=case.name):
                problem = parse_problem(case)
                depths = {problem.origin: 0}
                queue = deque([problem.origin])
                while queue:
                    source = queue.popleft()
                    for target, _ in problem.successors(source):
                        if target not in depths:
                            depths[target] = depths[source] + 1
                            queue.append(target)
                optimum = min((depths[g] for g in problem.destinations
                               if g in depths), default=None)
                result = cus2(problem)
                if optimum is None:
                    self.assertIsNone(result.goal)
                    continue
                self.assertIsNotNone(result.goal)
                self.assertEqual(result.goal.depth, optimum)
                path = result.goal.path()
                self.assertEqual(path[0], problem.origin)
                self.assertIn(path[-1], problem.destinations)
                self.assertEqual(len(path), len(set(path)))
                total = 0
                for source, target in zip(path, path[1:]):
                    edges = dict(problem.successors(source))
                    self.assertIn(target, edges)
                    total += edges[target]
                self.assertAlmostEqual(result.goal.path_cost, total)

    def test_fewer_moves_even_when_more_expensive(self):
        problem = parse_problem(Path(__file__).parent / 'cases/test06_cheap_long_vs_short_expensive.txt')
        result = cus2(problem)
        self.assertEqual(result.goal.path(), [1, 5, 4])
        self.assertEqual(result.goal.depth, 2)
        self.assertEqual(result.goal.path_cost, 40)

    def test_origin_goal_without_edges(self):
        result = cus2(RouteProblem({1: (0, 0)}, [], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_no_edges_unreachable(self):
        result = cus2(RouteProblem({1: (0, 0), 2: (1, 0)}, [], 1, {2}))
        self.assertIsNone(result.goal)
        self.assertEqual(result.nodes_created, 1)

    def test_coincident_coordinates_and_cycle(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 2, 1), (2, 1, 1), (2, 3, 1)], 1, {3})
        result = cus2(problem)
        self.assertEqual(result.goal.path(), [1, 2, 3])
        self.assertEqual(result.nodes_created, 4)

    def test_geometric_priority_before_node_id(self):
        problem = RouteProblem({1: (0, 0), 2: (-10, 0), 3: (9, 0), 4: (10, 0)},
                               [(1, 2, 1), (1, 3, 100), (2, 4, 1), (3, 4, 100)], 1, {4})
        self.assertEqual(cus2(problem).goal.path(), [1, 3, 4])

    def test_equal_priorities_use_sibling_order(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 3, 1), (1, 2, 9)], 1, {2, 3})
        self.assertEqual(cus2(problem).goal.path(), [1, 2])


if __name__ == '__main__':
    unittest.main()
