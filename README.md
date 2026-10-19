# COS30019 Assignment 2A – Tree-Based Search (Route Finding)

Due **11:59pm Sunday 25 Oct 2026**. Worth 40% of Assignment 2. Spec: `COS30019-2026 S2-A2_A.pdf`.

Find a path from an origin node to any one of the destination nodes on a directed, weighted 2D graph,
using six search methods implemented from scratch (no search libraries).

## Usage

Python 3, standard library only. Works from `cmd` on Windows 10/11:

```
python search.py <filename> <method>
search <filename> <method>          (via search.bat)
```

Methods: `DFS`, `BFS`, `GBFS`, `AS`, `CUS1`, `CUS2`

Output:

```
filename method
goal number_of_nodes
path
```

Run every method on every test case (add `--csv results.csv` to save data for the report):

```
python run_tests.py
```

Unit tests:

```
python -m unittest discover tests
```

## Project layout

| Path | What it is | Status |
|---|---|---|
| `search.py` / `search.bat` | CLI entry point, output formatting | done |
| `route_finding/parser.py` | Reads problem files into a `RouteProblem` | done |
| `route_finding/problem.py` | Graph, successors (ascending order), goal test, heuristic | done |
| `route_finding/node.py` | Search-tree `Node`, `expand()`, `SearchResult` | done |
| `route_finding/frontier.py` | Priority queue with the spec's tie-breaking | done |
| `route_finding/algorithms/dfs.py` | Depth-first search | implemented and tested |
| `route_finding/algorithms/bfs.py` | Breadth-first search | implemented and tested |
| `route_finding/algorithms/gbfs.py` | Greedy best-first search | implemented and tested |
| `route_finding/algorithms/astar.py` | A* search | implemented and tested |
| `route_finding/algorithms/cus1.py` | Uniform-cost search | implemented and tested |
| `route_finding/algorithms/cus2.py` | A* on move count | implemented and tested |
| `tests/cases/` | Problem files (need **at least 15**), described in `tests/cases/README.md` | 15 – done |
| `run_tests.py` | Batch runner / results table | done |

Each algorithm takes a `RouteProblem` and returns `SearchResult(goal_node_or_None, nodes_created)`.
The stubs contain hints for each method.

## Decisions to agree on as a team (and state in the report)

- **Tie-breaking (NOTE 2):** expand smaller node ids first, then chronological insertion order.
  `PriorityFrontier` uses `(priority, insertion_counter)` with children inserted in ascending order.
- **Cycles:** the graph has cycles (e.g. 1 ↔ 3). Pick a strategy – `node.on_path()` (pure tree search)
  or a visited set (graph search) – and apply it consistently.
- **number_of_nodes:** count every `Node` created, including the root.
- **Goal test timing:** on generation vs. on expansion (A* must test on expansion to stay optimal).
- **Heuristic:** straight-line distance to the nearest destination. Only admissible if edge costs are
  at least their Euclidean length – discuss in the report.

## Deliverables checklist

- [ ] All 6 methods working (10 marks each)
- [~] ≥ 15 test cases covering different scenarios (done), results documented (10)
- [ ] Report, 8–10 pages excl. cover/TOC, named `<TeamID>.pdf` (20)
  - cover page with names, IDs, signatures, contribution statement · TOC · instructions · introduction ·
    features/bugs/missing · testing · insights (with data) · research · conclusion ·
    acknowledgements/resources (incl. AI use) · references · captioned figures/tables · page numbers
- [ ] Research component, e.g. visit ALL destinations via the shortest path (10)
- [ ] Clean, commented code (up to −10 otherwise)
- [ ] At least two in-class progress meetings with the tutor, a week apart (`COS30019_a2_MeetingRecordForm.docx`)
- [ ] Who-did-what form (`COS30019 - Who did What.docx`)

## DFS implementation

DFS uses a LIFO stack, pushes siblings in descending node-id order so the
smallest is explored first, and tests for a goal when a node is popped.
It rejects nodes already on the current ancestor path to prevent cycles;
the same graph state may still be explored on different branches. This is
tree search with path cycle checking, not a global visited set.
Every Node created by expand() is counted, including rejected cycle nodes
and the root. DFS does not guarantee minimum cost or minimum moves and can
explore many simple paths on dense graphs.

On test01_spec_example.txt, DFS returns 2 1 3 5, cost 15, with 9 nodes
created. Run `python -m unittest discover tests -v` for DFS behaviour tests
and route/reachability checks over all 15 supplied cases.

## GBFS implementation

GBFS prioritizes straight-line distance to the nearest destination, ignoring
cost already paid. It uses PriorityFrontier with insertion-order ties and
ascending sibling insertion, and tests goals when popped. Like DFS, it uses
path cycle checking and counts every created Node, including rejected cycle
nodes and the root. Repeated states on different branches are allowed, so
large graphs may require substantial time and memory.

The example returns 2 3 5, cost 10, with 7 nodes created. In the greedy-trap
case it returns 1 2 5, cost 34, although 1 3 4 5 costs 18: GBFS does not
guarantee the cheapest route. The tests cover both examples, priority ties,
cycles, an origin already at a goal, and route validity/reachability across
all 15 fixtures.

## A* implementation

AS prioritizes f(n) = g(n) + h(n), where g is total edge cost so far and
h is scaled Euclidean distance to the nearest destination. The scale is
min(1, cost(u,v)/distance(u,v)) over all positive-length edges. Thus each
edge costs at least its scaled length, making h a lower bound on remaining
cost by the triangle inequality. Zero-cost positive-length edges make the
scale zero; A* then behaves as uniform-cost search. Coincident coordinates
need no ratio. Inputs are assumed to have finite coordinates and finite,
nonnegative costs.

Goals are tested when popped, not when generated. Path cycle checking,
node counting and insertion-order priority ties match GBFS. This tree search
can still explore many alternative simple paths on large graphs.
The example returns 2 3 5, cost 10, with 9 nodes created. A* results on all
15 fixtures are checked against independent Bellman-Ford minimum costs,
including unreachable goals and a case where raw Euclidean h overestimates.

## CUS1: uniform-cost search

CUS1 prioritizes g(n), the total edge cost already paid, without consulting
coordinates or a heuristic. For finite graphs with finite nonnegative edge
costs it returns a minimum-cost route to any destination, testing goals only
when removed from the priority queue. It uses path cycle checking, counts
all created Nodes (including the root and rejected cycle nodes), and uses
insertion-order ties with ascending sibling insertion, matching AS/GBFS.
This tree-search approach may explore many alternative paths and use large
amounts of memory. It does not minimize the number of moves.

On the supplied example CUS1 returns 2 1 4, cost 10, with 15 created nodes.
The A* route 2 3 5 has the same minimum cost. Tests compare CUS1 against an
independent Bellman-Ford cost oracle on all 15 fixtures and also cover
zero-cost cycles, equal-cost ties, origin-at-goal, goal-test timing,
coordinate independence, and cheaper routes requiring more moves.

## CUS2: informed search for fewest moves

CUS2 uses A* with g(n) = node depth and h(n) = Euclidean distance to the
nearest goal divided by the longest geometric edge length in the graph.
Since one move can cover at most that length, the estimate is a lower bound
on moves remaining. If all edges have zero length or there are no edges,
h is zero. Input coordinates are assumed finite. Travel costs are recorded
but do not affect priority: a route with fewer moves may cost more.

Goals are tested when popped. Path cycle checking, created-node counts and
priority ties match AS. Searching alternative simple paths can be expensive
on large graphs. Tests compare minimum moves with an independent breadth-
first distance calculation on all 15 fixtures; additional cases cover zero
lengths, no edges, cycles, goal origins, geometry-based priorities and ties.
All six methods now run through the 15 supplied cases (90 method/case runs).
BFS now counts every created Node, including rejected repeats and the root,
matching the other methods. BFS still uses a global reached set and tests
goals on generation; the others use path cycle checking and test goals on
removal. Performance comparisons therefore describe these implementations,
not just differences between textbook search strategies.


## Reproducible report evidence

Run `python benchmark_report.py` to validate all 90 method/case combinations
and write `results/comparison.md` and `results/benchmark.json`. It checks
reachability and route validity for every method, minimum cost for AS/CUS1,
and minimum moves for BFS/CUS2 using independent reference calculations.
Timing is the median of 30 runs after a warm-up, excluding input parsing.
The Markdown summary records interpretation limits and selected comparisons.
