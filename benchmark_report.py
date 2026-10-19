"""Validate all methods and generate reproducible report evidence."""
import json
import math
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from route_finding import parse_problem
from route_finding.algorithms import METHODS

ROOT = Path(__file__).resolve().parent
REPEATS = 30


def reference(problem):
    # Bellman-Ford relaxation, separately for edge cost and unit move cost.
    costs = dict.fromkeys(problem.nodes, math.inf)
    moves = dict.fromkeys(problem.nodes, math.inf)
    costs[problem.origin] = moves[problem.origin] = 0
    for _ in range(len(problem.nodes) - 1):
        for source in problem.nodes:
            for target, cost in problem.successors(source):
                costs[target] = min(costs[target], costs[source] + cost)
                moves[target] = min(moves[target], moves[source] + 1)
    return (min(costs[g] for g in problem.destinations),
            min(moves[g] for g in problem.destinations))


def check(problem, method, result, best_cost, best_moves):
    if math.isinf(best_cost):
        assert result.goal is None, 'Returned a goal for an unreachable problem'
        return
    assert result.goal is not None, 'Missed a reachable goal'
    path = result.goal.path()
    assert path[0] == problem.origin and path[-1] in problem.destinations
    assert len(path) == len(set(path)), 'Cycle in returned route'
    cost = 0
    for source, target in zip(path, path[1:]):
        edges = dict(problem.successors(source))
        assert target in edges, 'Invalid directed edge'
        cost += edges[target]
    assert math.isclose(cost, result.goal.path_cost)
    assert result.goal.depth == len(path) - 1
    if method == 'AS':
        assert math.isclose(cost, best_cost), 'Nonoptimal cost'
    if method in ('BFS', 'CUS1', 'CUS2'):
        assert result.goal.depth == best_moves, 'Nonoptimal move count'


def main():
    rows = []
    cases = sorted((ROOT / 'tests/cases').glob('test*.txt'))
    assert len(cases) >= 15
    for case in cases:
        problem = parse_problem(case)
        best_cost, best_moves = reference(problem)
        for method, algorithm in METHODS.items():
            result = algorithm(problem)  # Warm-up and correctness run.
            check(problem, method, result, best_cost, best_moves)
            durations = []
            for _ in range(REPEATS):
                start = time.perf_counter_ns()
                repeated = algorithm(problem)
                durations.append((time.perf_counter_ns() - start) / 1_000_000)
                assert repeated == result or (
                    repeated.nodes_created == result.nodes_created and
                    (repeated.goal.path() if repeated.goal else None) ==
                    (result.goal.path() if result.goal else None))
            goal = result.goal
            rows.append(dict(case=case.name, method=method, verified=True,
                             outcome='route found' if goal else 'correctly unreachable',
                             nodes_created=result.nodes_created,
                             cost=goal.path_cost if goal else None,
                             moves=goal.depth if goal else None,
                             path=goal.path() if goal else None,
                             median_ms=statistics.median(durations)))
    metadata = dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
                    python=platform.python_version(), platform=platform.platform(),
                    repetitions=REPEATS, timing='Median; parsing excluded; one warm-up')
    output = ROOT / 'results'
    output.mkdir(exist_ok=True)
    (output / 'benchmark.json').write_text(
        json.dumps(dict(metadata=metadata, results=rows), indent=2), encoding='utf-8')
    lines = ['# Search comparison evidence', '',
             f'All {len(rows)} method/case combinations passed independent correctness checks.',
             'A missing route is a correct outcome for the deliberately unreachable case.', '',
             '## Measurement method', '',
             f'- Timing: median of {REPEATS} runs after one warm-up; input parsing excluded.',
             '- Nodes: every created search Node, including root and rejected children; IDDFS/IDA* include regenerated roots and children across all iterations.',
             '- Cost: sum of directed edge costs; moves: number of edges in the route.',
             '- Reachability, route edges and reported costs checked for all methods.',
             '- Bellman-Ford reference checks minimum cost for AS and minimum moves for BFS/CUS1/CUS2.',
             '- BFS uses global duplicate suppression and goal tests on generation; other methods use path cycle checks; custom methods use depth-first iterations within limits.',
             '- These comparisons describe the implemented variants, not isolated algorithm effects.',
             '- Small timings are sensitive to system load; memory usage was not measured.',
             '- Fifteen small cases do not establish general scalability or a universal fastest method.', '',
             '## Supplied example', '',
             '| Method | Route | Cost | Moves | Nodes created |',
             '|---|---|---:|---:|---:|']
    for r in rows:
        if r['case'].startswith('test01_'):
            lines.append(f"| {r['method']} | {' -> '.join(map(str, r['path']))} | {r['cost']} | {r['moves']} | {r['nodes_created']} |")
    lines += ['', '## Useful findings for the report', '',
              '- Cheap-long versus expensive-short: compare BFS/CUS1/CUS2 with AS to explain moves versus cost.',
              '- Greedy trap: GBFS chooses a route costing 34; a cheapest route costs 18.',
              '- Misleading geometry: scaled A* still finds cost 2 despite raw Euclidean distance overestimating.',
              '- Grid: compare IDDFS and IDA* counts to discuss repeated work and heuristic guidance; they target moves, unlike AS.',
              '- Unreachable case: all methods must return no route; that is not an algorithm failure.',
              '- Original BFS example count was 4; corrected count is 5 because a generated duplicate also creates a Node.', '',
              '## Complete measured results', '',
              '| Case | Method | Outcome | Cost | Moves | Nodes | Median ms |',
              '|---|---|---|---:|---:|---:|---:|']
    for r in rows:
        cost = r['cost'] if r['cost'] is not None else 'N/A'
        moves = r['moves'] if r['moves'] is not None else 'N/A'
        lines.append(f"| {r['case']} | {r['method']} | {r['outcome']} | {cost} | {moves} | {r['nodes_created']} | {r['median_ms']:.4f} |")
    lines += ['', '## Remaining submission work', '',
              '- Write the 8-10 page report with actual team details, contributions and AI-use acknowledgement.',
              '- Add properly sourced algorithm explanations and references.',
              '- Decide and document the research component; do not claim GUI validation or memory experiments that were not performed.',
              '- Confirm tie-breaking interpretation and choice of custom methods with course guidance.',
              '- Complete team signatures and required tutor progress records.']
    (output / 'comparison.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Validated {len(rows)} results; saved results/comparison.md and results/benchmark.json')


if __name__ == '__main__':
    main()
