"""Research experiments used in the report (Section 7).

Usage:
    python research/experiments.py            # writes results/research.json

1. Heuristic ablation: A* with the raw straight-line heuristic versus the
   scaled heuristic used by AS, on all 15 test cases.
2. Scalability: all six methods on random geometric graphs of growing size.
3. Visit-all destinations: state-space A* vs pairwise legs + Held-Karp vs a
   greedy nearest-destination baseline.
Random graphs use fixed seeds so every run gives the same graphs.
"""

import json
import math
import os
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from route_finding import parse_problem                          # noqa: E402
from route_finding.problem import RouteProblem                   # noqa: E402
from route_finding.algorithms import METHODS                     # noqa: E402
import importlib                                                 # noqa: E402
astar_module = importlib.import_module("route_finding.algorithms.astar")
from visit_all import visit_all_greedy, visit_all_legs, visit_all_state_space  # noqa: E402


def dijkstra_reference(problem, source, unit=False):
    """Bellman-Ford style reference (small graphs): min cost (or moves) to every node."""
    dist = dict.fromkeys(problem.nodes, math.inf)
    dist[source] = 0
    for _ in range(len(problem.nodes) - 1):
        changed = False
        for s in problem.nodes:
            for t, c in problem.successors(s):
                v = dist[s] + (1 if unit else c)
                if v < dist[t]:
                    dist[t], changed = v, True
        if not changed:
            break
    return dist


def random_problem(n, seed, n_dest=1, k=3):
    """Random geometric graph: each node links to its k nearest neighbours.

    Each direction is kept with probability 0.8 (so some edges are one-way).
    Cost = ceil(length * U(1.0, 1.6)), so costs never undercut geometry.
    Origin and destinations are chosen among mutually reachable nodes.
    """
    rng = random.Random(seed)
    while True:
        nodes = {i: (rng.randint(0, 100), rng.randint(0, 100)) for i in range(1, n + 1)}
        edges = set()
        for a in nodes:
            near = sorted((b for b in nodes if b != a),
                          key=lambda b: math.dist(nodes[a], nodes[b]))[:k]
            for b in near:
                length = math.dist(nodes[a], nodes[b])
                for s, t in ((a, b), (b, a)):
                    if rng.random() < 0.8:
                        edges.add((s, t, max(1, math.ceil(length * rng.uniform(1.0, 1.6)))))
        best = {}
        for s, t, c in edges:
            best[s, t] = min(c, best.get((s, t), math.inf))
        edges = [(s, t, c) for (s, t), c in best.items()]
        origin = rng.choice(list(nodes))
        probe = RouteProblem(nodes, edges, origin, [origin])
        reach = [v for v, d in dijkstra_reference(probe, origin).items()
                 if d < math.inf and v != origin]
        if len(reach) >= max(n // 2, n_dest):
            far = sorted(reach, key=lambda v: -math.dist(nodes[origin], nodes[v]))
            dests = rng.sample(far[:max(n_dest, len(far) // 2)], n_dest)
            return RouteProblem(nodes, edges, origin, dests)


def timed(fn, problem, repeats=5):
    out, times = None, []
    for _ in range(repeats):
        start = time.perf_counter()
        out = fn(problem)
        times.append((time.perf_counter() - start) * 1000)
    return out, statistics.median(times)


def heuristic_ablation():
    rows = []
    original = astar_module.heuristic_scale
    for case in sorted((ROOT / "tests" / "cases").glob("test*.txt")):
        problem = parse_problem(case)
        ref = dijkstra_reference(problem, problem.origin)
        best = min(ref[d] for d in problem.destinations)
        scaled = METHODS["AS"](problem)
        astar_module.heuristic_scale = lambda p: 1.0          # raw Euclidean h
        try:
            raw = astar_module.astar(problem)
        finally:
            astar_module.heuristic_scale = original
        rows.append(dict(case=case.name, optimal=None if best == math.inf else best,
                         scale=round(original(problem), 4),
                         raw_cost=raw.goal.path_cost if raw.goal else None,
                         raw_nodes=raw.nodes_created,
                         scaled_cost=scaled.goal.path_cost if scaled.goal else None,
                         scaled_nodes=scaled.nodes_created))
    return rows


def scalability(sizes=(10, 20, 30, 40, 50, 60), instances=12):
    rows = []
    for n in sizes:
        for i in range(instances):
            problem = random_problem(n, seed=1000 * n + i)
            ref_cost = dijkstra_reference(problem, problem.origin)
            ref_moves = dijkstra_reference(problem, problem.origin, unit=True)
            best_cost = min(ref_cost[d] for d in problem.destinations)
            best_moves = min(ref_moves[d] for d in problem.destinations)
            for name, fn in METHODS.items():
                result, ms = timed(fn, problem)
                rows.append(dict(n=n, instance=i, method=name,
                                 nodes=result.nodes_created, ms=ms,
                                 cost_ratio=result.goal.path_cost / best_cost,
                                 moves_ratio=result.goal.depth / best_moves))
    return rows


def visit_all_experiment(k_values=(2, 3, 4, 5, 6), instances=10, n=25):
    rows = []
    for k in k_values:
        done = 0
        seed = 0
        while done < instances:
            seed += 1
            problem = random_problem(n, seed=50000 + 100 * k + seed, n_dest=k)
            (r1, c1, n1), t1 = timed(visit_all_state_space, problem, 3)
            if r1 is None:
                continue                      # some destination unreachable
            (r2, c2, n2), t2 = timed(visit_all_legs, problem, 3)
            r3, c3 = visit_all_greedy(problem)
            assert math.isclose(c1, c2), (c1, c2)
            assert set(problem.destinations) <= set(r1) and set(problem.destinations) <= set(r2)
            rows.append(dict(k=k, state_nodes=n1, state_ms=t1, legs_nodes=n2, legs_ms=t2,
                             optimal=c1, greedy=c3))
            done += 1
    return rows


def main():
    data = dict(heuristic=heuristic_ablation(), scalability=scalability(),
                visit_all=visit_all_experiment())
    out = ROOT / "results" / "research.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
