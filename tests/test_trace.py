"""The expansion tracer used by the GUI records real expansions only."""

import unittest

from helpers import fixture_paths, load_case
from route_finding import parse_problem
from route_finding.algorithms import METHODS
from route_finding.trace import trace_search


class TraceTests(unittest.TestCase):
    def test_bfs_example_steps(self):
        result, steps = trace_search(load_case("test01_spec_example.txt"), METHODS["BFS"])
        self.assertEqual(steps, [(2, [1, 3]), (1, [3, 4])])
        self.assertEqual(result.goal.path(), [2, 1, 4])

    def test_tracing_does_not_change_results(self):
        problem = load_case("test13_large_grid.txt")
        for name, method in METHODS.items():
            with self.subTest(method=name):
                plain = method(problem)
                traced, _ = trace_search(problem, method)
                self.assertEqual(traced.nodes_created, plain.nodes_created)
                self.assertEqual(traced.goal.path(), plain.goal.path())

    def test_logged_children_match_nodes_created(self):
        # Every created node is either a root or a child logged by the tracer.
        # The old tracer logged IDDFS cutoff checks as expansions and broke this.
        for case in fixture_paths():
            problem = parse_problem(case)
            for name, method in METHODS.items():
                with self.subTest(case=case.name, method=name):
                    result, steps = trace_search(problem, method)
                    children = sum(len(kids) for _, kids in steps)
                    roots = result.nodes_created - children
                    self.assertGreaterEqual(roots, 1)
                    if name not in ("CUS1", "CUS2"):  # only iterative methods recreate the root
                        self.assertEqual(roots, 1)

    def test_original_expand_is_restored(self):
        import sys
        from route_finding.node import expand
        # The package re-exports the dfs function under the same name as its
        # module, so look the module up directly.
        dfs_module = sys.modules["route_finding.algorithms.dfs"]
        trace_search(load_case("test01_spec_example.txt"), METHODS["DFS"])
        self.assertIs(dfs_module.expand, expand)


if __name__ == "__main__":
    unittest.main()
