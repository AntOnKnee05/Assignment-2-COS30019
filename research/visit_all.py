"""Research extension: visit ALL destination nodes with the lowest total cost.

Usage:
    python research/visit_all.py <filename> [STATE|LEGS]

Two solvers are provided so that they can check each other:

STATE  A* over an augmented state (node, destinations still to visit).
       The goal is any state whose "to visit" set is empty. The heuristic
       is the scaled straight-line distance to the FARTHEST unvisited
       destination, which never overestimates because every remaining
       destination must still be reached.

LEGS   Decompose the tour into legs. Run the group's single-goal A* between
       every pair of key points (origin + destinations), then choose the
       cheapest visiting order with Held-Karp dynamic programming. Legs are
       directed, so cost(a->b) may differ from cost(b->a).

Both return the full node-by-node route. A destination passed through on
the way to another counts as visited.
"""

import itertools
import os
import sys
from math import inf

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_finding import Node, parse_problem                    # noqa: E402
from route_finding.frontier import PriorityFrontier               # noqa: E402
from route_finding.problem import RouteProblem                    # noqa: E402
from route_finding.algorithms.astar import astar, heuristic_scale  # noqa: E402


def _edges(problem):
    """Rebuild the edge list from the adjacency lists."""
    return [(s, t, c) for s in problem.nodes for t, c in problem.successors(s)]


def visit_all_state_space(problem):
    """A* on (node, frozenset of unvisited destinations).

    Returns (route, cost, nodes_created); route is None if impossible.
    Graph search with a best-g table is used because the augmented space
    grows as V * 2^k and pure path-checking tree search repeats too much.
    """
    scale = heuristic_scale(problem)
    todo0 = frozenset(problem.destinations - {problem.origin})

    def h(state, todo):
        return scale * max((problem.distance(state, d) for d in todo), default=0.0)

    root = Node((problem.origin, todo0))
    created = 1
    best_g = {root.state: 0}
    frontier = PriorityFrontier()
    frontier.push(root, h(problem.origin, todo0))
    while frontier:
        node = frontier.pop()
        state, todo = node.state
        if not todo:
            route = [s for s, _ in node.path()]
            return route, node.path_cost, created
        if node.path_cost > best_g.get(node.state, inf):
            continue                       # stale entry, a cheaper copy exists
        for nxt, cost in problem.successors(state):
            child = Node((nxt, todo - {nxt}), node, node.path_cost + cost)
            created += 1
            if child.path_cost < best_g.get(child.state, inf):
                best_g[child.state] = child.path_cost
                frontier.push(child, child.path_cost + h(*child.state))
    return None, None, created


def visit_all_legs(problem):
    """Pairwise A* legs + Held-Karp ordering. Returns (route, cost, nodes_created)."""
    edges = _edges(problem)
    dests = sorted(problem.destinations - {problem.origin})
    keys = [problem.origin] + dests
    leg = {}
    created = 0
    for a, b in itertools.permutations(keys, 2):
        if b == problem.origin:
            continue                        # never need to return to the start
        result = astar(RouteProblem(problem.nodes, edges, a, [b]))
        created += result.nodes_created
        leg[a, b] = (result.goal.path_cost, result.goal.path()) if result.goal else (inf, None)

    # Held-Karp: best[(visited mask, last)] = (cost, previous key)
    n = len(dests)
    best = {(1 << i, i): (leg[problem.origin, dests[i]][0], None) for i in range(n)}
    for mask in range(1, 1 << n):
        for last in range(n):
            if (mask, last) not in best:
                continue
            cost, _ = best[mask, last]
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue
                new = (mask | (1 << nxt), nxt)
                value = cost + leg[dests[last], dests[nxt]][0]
                if value < best.get(new, (inf, None))[0]:
                    best[new] = (value, last)
    if n == 0:
        return [problem.origin], 0, created
    full = (1 << n) - 1
    last = min(range(n), key=lambda i: best.get((full, i), (inf,))[0])
    total = best.get((full, last), (inf,))[0]
    if total == inf:
        return None, None, created

    order, mask = [], full                  # walk back through the table
    while last is not None:
        order.append(dests[last])
        prev = best[mask, last][1]
        mask &= ~(1 << last)
        last = prev
    order.reverse()
    route = [problem.origin]
    for a, b in zip([problem.origin] + order, order):
        route += leg[a, b][1][1:]
    return route, total, created


def visit_all_greedy(problem):
    """Baseline: repeatedly go to the cheapest unvisited destination."""
    edges = _edges(problem)
    current, todo = problem.origin, set(problem.destinations - {problem.origin})
    route, total = [problem.origin], 0
    while todo:
        result = astar(RouteProblem(problem.nodes, edges, current, todo))
        if result.goal is None:
            return None, None
        route += result.goal.path()[1:]
        total += result.goal.path_cost
        todo -= set(result.goal.path())
        current = result.goal.state
    return route, total


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    problem = parse_problem(argv[1])
    solver = visit_all_legs if len(argv) == 3 and argv[2].upper() == "LEGS" else visit_all_state_space
    route, cost, created = solver(problem)
    print(f"{argv[1]} VISIT-ALL")
    if route is None:
        print(f"Not every destination is reachable; {created}")
    else:
        print(f"cost {cost} nodes {created}")
        print(" ".join(map(str, route)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
