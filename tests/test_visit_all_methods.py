"""Visit-all versions of the six required methods (DFS-ALL ... CUS2-ALL).

Routes are checked against the brute-force reference in test_visit_all,
which never calls the search code. AS-ALL must match the cheapest cost.
BFS-ALL, CUS1-ALL and CUS2-ALL must match the fewest moves, found with the
same reference on a copy of the map where every edge costs 1. DFS-ALL and
GBFS-ALL need only return a valid route, just like DFS and GBFS.
"""

import os
import subprocess
import sys
import unittest

from test_visit_all import ALL_CASES, PROJECT, all_problems, brute_force_cost
from route_finding import parse_problem
from route_finding.algorithms import METHODS, RESEARCH_METHODS
from route_finding.algorithms.visit_all_methods import VisitAllProblem, VisitState
from route_finding.problem import RouteProblem
from route_finding.trace import TraceLimitExceeded, trace_search

VARIANTS = {f"{name}-ALL": RESEARCH_METHODS[f"{name}-ALL"] for name in METHODS}
FEWEST_MOVES = ("BFS-ALL", "CUS1-ALL", "CUS2-ALL")
# Tree search over (location, visited) states: IDDFS on the five-destination
# grid creates over 60 million nodes, so it is left out to keep the suite fast.
TOO_SLOW = {("CUS1-ALL", "all05_grid_five_destinations.txt")}


def unit_cost_copy(problem):
    edges = [(s, t, 1) for s in problem.nodes for t, _ in problem.successors(s)]
    return RouteProblem(problem.nodes, edges, problem.origin, problem.destinations)


class VisitAllMethodTests(unittest.TestCase):
    def assertValidTour(self, problem, result):
        """A real walk from the origin that visits every destination; returns (cost, moves)."""
        path = result.goal.path()
        self.assertEqual(path[0], problem.origin)
        self.assertTrue(problem.destinations <= set(path), "a destination was skipped")
        self.assertEqual(result.goal.state, path[-1])
        self.assertIn(path[-1], problem.destinations)
        cost = 0
        for source, target in zip(path, path[1:]):
            edges = dict(problem.successors(source))
            self.assertIn(target, edges, f"no directed edge {source}->{target}")
            cost += edges[target]
        self.assertAlmostEqual(result.goal.path_cost, cost)
        self.assertEqual(result.goal.depth, len(path) - 1)
        return cost, len(path) - 1

    def test_every_variant_on_every_map(self):
        for name, problem in all_problems():
            optimum = brute_force_cost(problem)
            fewest = brute_force_cost(unit_cost_copy(problem))
            for method, search in VARIANTS.items():
                if (method, name) in TOO_SLOW:
                    continue
                with self.subTest(case=name, method=method):
                    result = search(problem)
                    if optimum is None:
                        self.assertIsNone(result.goal)
                        continue
                    cost, moves = self.assertValidTour(problem, result)
                    if method == "AS-ALL":
                        self.assertAlmostEqual(cost, optimum)
                    if method in FEWEST_MOVES:
                        self.assertEqual(moves, fewest)

    def test_dead_end_is_revisited_by_every_variant(self):
        problem = parse_problem(ALL_CASES / "all01_dead_end.txt")
        for method, search in VARIANTS.items():
            with self.subTest(method=method):
                self.assertEqual(search(problem).goal.path(), [1, 2, 3, 2, 4, 5])

    def test_as_all_matches_research_all_method(self):
        for name, problem in all_problems():
            with self.subTest(case=name):
                a, b = VARIANTS["AS-ALL"](problem), RESEARCH_METHODS["ALL"](problem)
                if b.goal is None:
                    self.assertIsNone(a.goal)
                else:
                    self.assertAlmostEqual(a.goal.path_cost, b.goal.path_cost)

    def test_variant_differs_from_single_goal_method(self):
        # The spec example has destinations 5 and 4: BFS stops at 4, BFS-ALL goes on to 5.
        problem = parse_problem(PROJECT / "tests/cases/test01_spec_example.txt")
        self.assertEqual(METHODS["BFS"](problem).goal.path(), [2, 1, 4])
        self.assertEqual(VARIANTS["BFS-ALL"](problem).goal.path(), [2, 1, 4, 5])

    def test_origin_only_destination(self):
        problem = RouteProblem({1: (0, 0), 2: (1, 0)}, [(1, 2, 1)], 1, {1})
        for method, search in VARIANTS.items():
            with self.subTest(method=method):
                result = search(problem)
                self.assertEqual(result.goal.path(), [1])
                self.assertEqual(result.nodes_created, 1)

    def test_heuristic_is_zero_once_everything_is_visited(self):
        wrapped = VisitAllProblem(parse_problem(ALL_CASES / "all01_dead_end.txt"))
        for state in wrapped.nodes:
            with self.subTest(state=state):
                self.assertEqual(wrapped.heuristic(state) == 0, wrapped.is_goal(state))


class VisitAllTraceTests(unittest.TestCase):
    """The GUI replays these methods through route_finding.trace."""

    def test_tracing_does_not_change_results(self):
        problem = parse_problem(ALL_CASES / "all02_greedy_trap.txt")
        for method, search in {**VARIANTS, "ALL": RESEARCH_METHODS["ALL"]}.items():
            with self.subTest(method=method):
                plain = search(problem)
                traced, steps = trace_search(problem, search)
                self.assertTrue(steps, "no expansions were recorded")
                self.assertEqual(traced.nodes_created, plain.nodes_created)
                self.assertEqual(traced.goal.path(), plain.goal.path())

    def test_logged_states_carry_the_visited_set(self):
        problem = parse_problem(ALL_CASES / "all01_dead_end.txt")
        _, steps = trace_search(problem, VARIANTS["BFS-ALL"])
        first, children = steps[0]
        self.assertEqual(first, VisitState(1, frozenset()))
        self.assertTrue(all(isinstance(c, VisitState) for c in children))

    def test_logged_children_match_nodes_created(self):
        problem = parse_problem(ALL_CASES / "all02_greedy_trap.txt")
        for method, search in VARIANTS.items():
            with self.subTest(method=method):
                result, steps = trace_search(problem, search)
                roots = result.nodes_created - sum(len(kids) for _, kids in steps)
                self.assertGreaterEqual(roots, 1)
                if method not in ("CUS1-ALL", "CUS2-ALL"):
                    self.assertEqual(roots, 1)

    def test_step_limit_stops_a_huge_search(self):
        problem = parse_problem(ALL_CASES / "all05_grid_five_destinations.txt")
        with self.assertRaises(TraceLimitExceeded):
            trace_search(problem, VARIANTS["CUS1-ALL"], max_steps=1000)
        # The real expand() is put back even though the search was abandoned.
        from route_finding.node import expand
        self.assertIs(sys.modules["route_finding.algorithms.cus1"].expand, expand)


class VisitAllCommandLineTests(unittest.TestCase):
    def run_search(self, *args):
        return subprocess.run([sys.executable, "search.py", *args],
                              cwd=PROJECT, capture_output=True, text=True)

    def test_every_variant_runs(self):
        case = os.path.join("tests", "visit_all_cases", "all01_dead_end.txt")
        for method in VARIANTS:
            with self.subTest(method=method):
                proc = self.run_search(case, method.lower())
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(proc.stdout.splitlines()[0], f"{case} {method}")
                self.assertEqual(proc.stdout.splitlines()[2], "1 2 3 2 4 5")

    def test_unreachable_message(self):
        proc = self.run_search(os.path.join("tests", "visit_all_cases", "all03_unreachable.txt"),
                               "DFS-ALL")
        self.assertIn("Not every destination is reachable", proc.stdout)


if __name__ == "__main__":
    unittest.main()
