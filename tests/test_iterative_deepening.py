"""Checks that custom methods deepen, terminate and count actual records."""
import importlib
import unittest
from unittest.mock import patch
from route_finding.node import Node
from route_finding.problem import RouteProblem


class IterativeDeepeningTests(unittest.TestCase):
    def record_search(self, method, problem):
        module = importlib.import_module('route_finding.algorithms.' + method)
        records = []
        def make_node(*args, **kwargs):
            node = Node(*args, **kwargs)
            records.append(node)
            return node
        with patch.object(module, 'Node', side_effect=make_node), patch(
                'route_finding.node.Node', side_effect=make_node):
            result = getattr(module, method)(problem)
        self.assertEqual(result.nodes_created, len(records))
        return result, records

    def test_iterations_count_roots_and_regenerated_children(self):
        problem = RouteProblem({i: (0, 0) for i in [1, 2, 3]},
                               [(1, 2, 1), (2, 3, 1)], 1, {3})
        for method, expected in [('cus1', 6), ('cus2', 8)]:
            with self.subTest(method=method):
                result, records = self.record_search(method, problem)
                self.assertEqual(result.goal.path(), [1, 2, 3])
                self.assertEqual(sum(n.parent is None for n in records), 3)
                self.assertEqual(result.nodes_created, expected)

    def test_unreachable_cycle_exhausts(self):
        problem = RouteProblem({i: (i, 0) for i in range(1, 8)},
                               [(1, 2, 0), (2, 1, 0), (2, 2, 0)], 1, {7})
        for method in ['cus1', 'cus2']:
            with self.subTest(method=method):
                result, records = self.record_search(method, problem)
                self.assertIsNone(result.goal)
                self.assertLessEqual(sum(n.parent is None for n in records), 3)

    def test_ida_star_jumps_to_smallest_exceeded_fractional_value(self):
        problem = RouteProblem({1: (0, 0), 2: (0, 4), 3: (3, 0)},
                               [(1, 2, 1), (2, 3, 1)], 1, {3})
        result, records = self.record_search('cus2', problem)
        # Initial threshold .6; child's f is 1 + 5/5 = 2. Jump directly to 2.
        self.assertEqual(sum(n.parent is None for n in records), 2)
        self.assertEqual(result.goal.depth, 2)
        self.assertEqual(result.nodes_created, 5)

    def test_ida_star_does_not_use_python_recursion(self):
        from route_finding.algorithms.cus2 import cus2
        size = 1100
        problem = RouteProblem({i: (i, 0) for i in range(size)},
                               [(i, i + 1, 1) for i in range(size - 1)], 0, {size - 1})
        result = cus2(problem)
        self.assertEqual(result.goal.depth, size - 1)
        self.assertEqual(result.nodes_created, size)
