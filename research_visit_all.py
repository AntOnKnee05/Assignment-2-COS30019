"""Experiments for the research extension (visit ALL destinations).

Run from the project folder:  python research_visit_all.py

Writes results/visit_all.md and results/visit_all.json. It compares:

1. ALL (A* over (location, visited set) states) with each of its three
   heuristics: "mst" (default), "farthest" and "none", to measure what a
   stronger estimate saves.
2. Two simpler ideas that look reasonable but fail, which motivated the design:
   * "nearest destination first": repeatedly take the cheapest path to the
     closest unvisited destination. Fast, but not optimal.
   * "location-only cycle check": the same state search, but rejecting any
     location already on the route, as the required methods do. It cannot
     find routes that must pass through a location twice.
3. How the work grows as the number of destinations increases.
"""

import heapq
import json
import math
import statistics
import time
from pathlib import Path

from route_finding import parse_problem
from route_finding.algorithms.astar import heuristic_scale
from route_finding.algorithms.visit_all import HEURISTICS, visit_all
from route_finding.frontier import PriorityFrontier
from route_finding.node import Node
from route_finding.problem import RouteProblem

ROOT = Path(__file__).resolve().parent
REPEATS = 5


def cheapest_costs(problem, source):
    """Dijkstra: cheapest cost from source to every reachable location."""
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


def nearest_first_cost(problem):
    """Greedy tour: always travel to the cheapest-to-reach unvisited destination."""
    here, total = problem.origin, 0
    left = set(problem.destinations) - {here}
    while left:
        costs = cheapest_costs(problem, here)
        reachable = [g for g in left if g in costs]
        if not reachable:
            return None
        here = min(reachable, key=lambda g: (costs[g], g))
        total += costs[here]
        left.discard(here)
    return total


def location_only_cost(problem):
    """The ALL state search, but rejecting any location already on the route."""
    goals = sorted(problem.destinations)
    bit = {g: 1 << i for i, g in enumerate(goals)}
    full = (1 << len(goals)) - 1
    root = Node(problem.origin)
    frontier = PriorityFrontier()
    frontier.push((root, bit.get(root.state, 0)), 0)
    while frontier:
        node, visited = frontier.pop()
        if visited == full:
            return node.path_cost
        for state, cost in problem.successors(node.state):
            if not node.on_path(state):
                child = Node(state, node, node.path_cost + cost)
                frontier.push((child, visited | bit.get(state, 0)), child.path_cost)
    return None


def timed(function, *args):
    durations = []
    for _ in range(REPEATS):
        start = time.perf_counter()
        result = function(*args)
        durations.append((time.perf_counter() - start) * 1000)
    return result, statistics.median(durations)


def grid(n, goals, origin=1):
    """n x n grid, four-way moves, costs 1-5 (always at least the edge length)."""
    nodes = {i + 1: (i % n, i // n) for i in range(n * n)}
    edges = []
    for i in range(n * n):
        x, y = i % n, i // n
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < n and 0 <= Y < n:
                edges.append((i + 1, Y * n + X + 1, 1 + (i * 7 + X) % 5))
    return RouteProblem(nodes, edges, origin, goals)


def main():
    maps = [ROOT / "tests/cases/test01_spec_example.txt",
            ROOT / "tests/cases/test07_multiple_destinations.txt",
            ROOT / "tests/cases/test15_equal_cost_tie.txt",
            *sorted((ROOT / "tests/visit_all_cases").glob("all0[1-2]*.txt")),
            ROOT / "tests/visit_all_cases/all05_grid_five_destinations.txt"]
    comparison = []
    for path in maps:
        problem = parse_problem(path)
        runs = {h: timed(visit_all, problem, h) for h in HEURISTICS}
        best = runs["mst"][0]
        if best.goal is None:
            continue  # no tour visits every destination on this map
        for h, (result, _) in runs.items():
            assert math.isclose(result.goal.path_cost, best.goal.path_cost), h
        comparison.append(dict(
            case=path.name, destinations=len(problem.destinations),
            optimal_cost=best.goal.path_cost, route=best.goal.path(),
            revisits=len(best.goal.path()) - len(set(best.goal.path())),
            nodes={h: runs[h][0].nodes_created for h in HEURISTICS},
            ms={h: runs[h][1] for h in HEURISTICS},
            nearest_first_cost=nearest_first_cost(problem),
            location_only_cost=location_only_cost(problem)))

    # Growth with the number of destinations on a 10 x 10 grid.
    spread = [100, 10, 91, 55, 28, 73, 46, 64, 19]
    growth = []
    for k in range(1, len(spread) + 1):
        problem = grid(10, spread[:k])
        runs = {h: timed(visit_all, problem, h) for h in HEURISTICS}
        for h, (result, _) in runs.items():
            assert math.isclose(result.goal.path_cost, runs["mst"][0].goal.path_cost), h
        growth.append(dict(destinations=k, states=100 * 2 ** k,
                           optimal_cost=runs["mst"][0].goal.path_cost,
                           nodes={h: runs[h][0].nodes_created for h in HEURISTICS},
                           ms={h: runs[h][1] for h in HEURISTICS}))

    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "visit_all.json").write_text(json.dumps(
        dict(comparison=comparison, growth=growth, repeats=REPEATS), indent=2), encoding="utf-8")

    def fmt(value):
        return "fails" if value is None else f"{value:g}"

    lines = ["# Visit-all-destinations research results", "",
             f"Times are the median of {REPEATS} runs. Every optimal cost matches the brute-force",
             "reference in tests/test_visit_all.py. Nodes = search nodes created.", "",
             "## Optimal tour versus simpler approaches", "",
             "| Case | Dest. | Optimal cost | Revisits | Nearest-first cost | Location-only check | Nodes (mst) | Nodes (farthest) | Nodes (none) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in comparison:
        n = r["nodes"]
        lines.append(f"| {r['case']} | {r['destinations']} | {fmt(r['optimal_cost'])} | {r['revisits']} | "
                     f"{fmt(r['nearest_first_cost'])} | {fmt(r['location_only_cost'])} | "
                     f"{n['mst']:,} | {n['farthest']:,} | {n['none']:,} |")
    lines += ["", "## Growth with the number of destinations (10 x 10 grid)", "",
              "| Destinations | Possible states | Optimal cost | Nodes (mst) | Nodes (farthest) | Nodes (none) | ms (mst) | ms (farthest) | ms (none) |",
              "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in growth:
        n, t = r["nodes"], r["ms"]
        lines.append(f"| {r['destinations']} | {r['states']:,} | {fmt(r['optimal_cost'])} | "
                     f"{n['mst']:,} | {n['farthest']:,} | {n['none']:,} | "
                     f"{t['mst']:.1f} | {t['farthest']:.1f} | {t['none']:.1f} |")
    (out / "visit_all.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
