"""Research extension (ALL): the cheapest route visiting every destination.

Results are checked against a brute-force reference that does not use the
search code: Dijkstra gives the cheapest cost between each pair of points,
and every possible ORDER of destinations is tried. The cheapest order's
total is the true optimum, because the best tour visits the destinations in
some first-visit order and can use the cheapest path between consecutive ones.
"""

import heapq
import itertools
import math
import os
import subprocess
import sys
import unittest
from pathlib import Path

from helpers import fixture_paths
from route_finding import parse_problem
from route_finding.algorithms import RESEARCH_METHODS
from route_finding.algorithms.visit_all import HEURISTICS, visit_all
from route_finding.problem import RouteProblem

ALL_CASES = Path(__file__).parent / "visit_all_cases"
PROJECT = Path(__file__).resolve().parent.parent


def dijkstra(problem, source):
    costs = {source: 0}
    queue = [(0, source)]
    while queue:
        cost, state = heapq.heappop(queue)
        if cost > costs[state]:
            continue
        for target, step in problem.successors(state):
            if cost + step < costs.get(target, math.inf):
                costs[target] = cost + step
                heapq.heappush(queue, (cost + step, target))
    return costs


def brute_force_cost(problem):
    """Cheapest cost to visit every destination, or None if impossible."""
    goals = [g for g in sorted(problem.destinations) if g != problem.origin]
    legs = {p: dijkstra(problem, p) for p in [problem.origin, *goals]}
    best = math.inf
    for order in itertools.permutations(goals):
        stops = [problem.origin, *order]
        best = min(best, sum(legs[a].get(b, math.inf) for a, b in zip(stops, stops[1:])))
    return None if math.isinf(best) else best


def all_problems():
    """Research maps plus every required-method fixture (single and multiple goals)."""
    paths = sorted(ALL_CASES.glob("all*.txt")) + fixture_paths()
    return [(p.name, parse_problem(p)) for p in paths]


class VisitAllTests(unittest.TestCase):
    def assertValidTour(self, problem, result):
        """The route is a real walk from the origin that visits every destination."""
        path = result.goal.path()
        self.assertEqual(path[0], problem.origin)
        self.assertTrue(problem.destinations <= set(path), "a destination was skipped")
        self.assertIn(path[-1], problem.destinations)
        cost = 0
        for source, target in zip(path, path[1:]):
            edges = dict(problem.successors(source))
            self.assertIn(target, edges, f"no directed edge {source}->{target}")
            cost += edges[target]
        self.assertAlmostEqual(result.goal.path_cost, cost)
        return cost

    def test_matches_brute_force_on_every_map(self):
        for name, problem in all_problems():
            optimum = brute_force_cost(problem)
            for heuristic in HEURISTICS:
                with self.subTest(case=name, heuristic=heuristic):
                    result = visit_all(problem, heuristic)
                    if optimum is None:
                        self.assertIsNone(result.goal)
                    else:
                        self.assertAlmostEqual(self.assertValidTour(problem, result), optimum)

    def test_spec_example(self):
        result = visit_all(parse_problem(PROJECT / "tests/cases/test01_spec_example.txt"))
        self.assertEqual(result.goal.path(), [2, 1, 4, 5])
        self.assertEqual(result.goal.path_cost, 17)

    def test_dead_end_requires_revisiting_a_location(self):
        result = visit_all(parse_problem(ALL_CASES / "all01_dead_end.txt"))
        self.assertEqual(result.goal.path(), [1, 2, 3, 2, 4, 5])
        self.assertEqual(result.goal.path_cost, 10)

    def test_nearest_destination_first_is_not_optimal(self):
        result = visit_all(parse_problem(ALL_CASES / "all02_greedy_trap.txt"))
        self.assertEqual(result.goal.path(), [3, 2, 1, 2, 3, 4, 5, 6])
        self.assertEqual(result.goal.path_cost, 7)  # nearest-first costs 8

    def test_unreachable_destination_means_no_solution(self):
        self.assertIsNone(visit_all(parse_problem(ALL_CASES / "all03_unreachable.txt")).goal)

    def test_origin_counts_as_visited(self):
        result = visit_all(parse_problem(ALL_CASES / "all04_origin_is_destination.txt"))
        self.assertEqual(result.goal.path(), [1, 2, 3])

    def test_only_the_origin_is_a_destination(self):
        result = visit_all(RouteProblem({1: (0, 0), 2: (1, 0)}, [(1, 2, 1)], 1, {1}))
        self.assertEqual(result.goal.path(), [1])
        self.assertEqual(result.nodes_created, 1)

    def test_stronger_heuristics_do_less_work_for_the_same_answer(self):
        problem = parse_problem(ALL_CASES / "all05_grid_five_destinations.txt")
        mst, farthest, none = (visit_all(problem, h) for h in ("mst", "farthest", "none"))
        self.assertAlmostEqual(mst.goal.path_cost, none.goal.path_cost)
        self.assertAlmostEqual(farthest.goal.path_cost, none.goal.path_cost)
        self.assertLess(mst.nodes_created, farthest.nodes_created)
        self.assertLess(farthest.nodes_created, none.nodes_created)

    def test_cheap_edges_keep_every_heuristic_safe(self):
        problem = RouteProblem({1: (0, 0), 2: (10, 0), 3: (20, 0), 4: (30, 0)},
                               [(1, 2, 1), (2, 3, 1), (3, 4, 1), (1, 4, 50)], 1, {2, 3, 4})
        for heuristic in HEURISTICS:
            with self.subTest(heuristic=heuristic):
                self.assertEqual(visit_all(problem, heuristic).goal.path_cost, 3)

    def test_unknown_heuristic_rejected(self):
        with self.assertRaises(ValueError):
            visit_all(RouteProblem({1: (0, 0)}, [], 1, {1}), "magic")

    def test_command_line(self):
        proc = subprocess.run([sys.executable, "search.py",
                               os.path.join("tests", "visit_all_cases", "all01_dead_end.txt"), "all"],
                              cwd=PROJECT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.splitlines()[1:], ["5 8", "1 2 3 2 4 5"])

    def test_command_line_unreachable_message(self):
        proc = subprocess.run([sys.executable, "search.py",
                               os.path.join("tests", "visit_all_cases", "all03_unreachable.txt"), "ALL"],
                              cwd=PROJECT, capture_output=True, text=True)
        self.assertIn("Not every destination is reachable", proc.stdout)

    def test_registered_separately_from_required_methods(self):
        from route_finding.algorithms import METHODS
        self.assertIn("ALL", RESEARCH_METHODS)
        self.assertNotIn("ALL", METHODS)


if __name__ == "__main__":
    unittest.main()
