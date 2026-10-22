"""Shared helpers for the test suite.

The reference answers here are computed directly from the graph and never
call a search method from route_finding, so a bug in an algorithm cannot
also hide inside the check that is meant to catch it.
"""

import math
from collections import deque
from pathlib import Path

from route_finding import parse_problem

CASES_DIR = Path(__file__).parent / "cases"


def fixture_paths():
    """All problem files in tests/cases, in name order."""
    return sorted(CASES_DIR.glob("test*.txt"))


def load_case(name):
    """Parse one fixture by file name, e.g. load_case('test01_spec_example.txt')."""
    return parse_problem(CASES_DIR / name)


def reachable_states(problem):
    """Every state reachable from the origin (simple graph traversal)."""
    seen = {problem.origin}
    pending = [problem.origin]
    while pending:
        for state, _ in problem.successors(pending.pop()):
            if state not in seen:
                seen.add(state)
                pending.append(state)
    return seen


def min_moves(problem):
    """Fewest edges from the origin to any destination, or None if unreachable."""
    depths = {problem.origin: 0}
    queue = deque([problem.origin])
    while queue:
        source = queue.popleft()
        for target, _ in problem.successors(source):
            if target not in depths:
                depths[target] = depths[source] + 1
                queue.append(target)
    return min((depths[g] for g in problem.destinations if g in depths), default=None)


def min_cost(problem):
    """Cheapest total cost to any destination (Bellman-Ford), or None if unreachable."""
    costs = dict.fromkeys(problem.nodes, math.inf)
    costs[problem.origin] = 0
    for _ in range(len(problem.nodes) - 1):
        for source in problem.nodes:
            for target, cost in problem.successors(source):
                costs[target] = min(costs[target], costs[source] + cost)
    best = min(costs[g] for g in problem.destinations)
    return None if math.isinf(best) else best


class RouteAssertions:
    """Mixin for unittest.TestCase with a full check of a returned route."""

    def assertValidRoute(self, problem, result):
        """Check the route starts at the origin, ends at a destination, uses
        only directed edges, repeats no state, and reports the right cost and
        depth. Returns the recomputed route cost."""
        self.assertIsNotNone(result.goal, "expected a route, got none")
        path = result.goal.path()
        self.assertEqual(path[0], problem.origin)
        self.assertIn(path[-1], problem.destinations)
        self.assertEqual(len(path), len(set(path)), "route repeats a state")
        cost = 0
        for source, target in zip(path, path[1:]):
            edges = dict(problem.successors(source))
            self.assertIn(target, edges, f"no directed edge {source}->{target}")
            cost += edges[target]
        self.assertAlmostEqual(result.goal.path_cost, cost)
        self.assertEqual(result.goal.depth, len(path) - 1)
        return cost
