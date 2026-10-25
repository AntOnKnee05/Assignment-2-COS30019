# COS30019 Assignment 2A – Tree-Based Search (Route Finding)

Due **11:59pm Sunday 25 Oct 2026**. Worth 40% of Assignment 2. Spec: `COS30019-2026 S2-A2_A.pdf`.

Find a path from an origin node to any one of the destination nodes on a directed, weighted 2D graph,
using six search methods implemented from scratch (no search libraries).

## Usage

Python 3 is required. The CLI, tests and GUI use the standard library; the GUI also needs Tkinter (included with the standard Windows Python installer). Optional chart scripts use Matplotlib. Run commands from the project folder containing `search.py`, using Command Prompt or PowerShell:

```
python search.py <filename> <method>
.\search.bat <filename> <method>    (Windows batch launcher)
```

Methods: `DFS`, `BFS`, `GBFS`, `AS`, `CUS1`, `CUS2`, plus the research extension `ALL`
(cheapest route that visits every destination; the path may repeat locations) and a
visit-all version of each required method: `DFS-ALL`, `BFS-ALL`, `GBFS-ALL`, `AS-ALL`,
`CUS1-ALL`, `CUS2-ALL`. All of them can be picked in the GUI.

Output:

```
filename method
goal number_of_nodes
path
```

Run the six required methods on the 15 standard cases (90 runs). Research methods are separate and are not included by `run_tests.py`. Add `--csv results.csv` to save the table:

```
python run_tests.py
```

Unit tests:

```
python -m unittest discover tests
```

## Required methods

| Code | Algorithm | Objective |
|---|---|---|
| `DFS` | Depth-first search | Find a route; no optimality guarantee |
| `BFS` | Breadth-first search | Fewest moves |
| `GBFS` | Greedy best-first search | Find a route using distance estimates; no optimality guarantee |
| `AS` | A* | Lowest travel cost with the scaled heuristic |
| `CUS1` | Iterative deepening DFS (IDDFS) | Fewest moves |
| `CUS2` | Iterative deepening A* (IDA*) | Fewest moves |

The required methods stop at **any one** destination. A move is one directed
edge; travel cost is the sum of the edge costs. Node labels are locations,
not costs. `number_of_nodes` counts created search records, including the
root and rejected children; iterative deepening includes every iteration.

For example:

```text
python search.py tests/cases/test01_spec_example.txt AS
```

Expected output:

```text
tests/cases/test01_spec_example.txt AS
5 9
2 3 5
```

Here the destination is 5, nine search records were created, and the route
is 2 -> 3 -> 5. The route costs 10 and takes two moves; those two metrics
are shown in the GUI and benchmark tables, not added to the required CLI
output. Quote input paths containing spaces. No `--explain` option is used.

## Graphical interface

Start the viewer, optionally selecting an input and method:

```text
python gui.py
python gui.py tests/cases/test01_spec_example.txt AS
python gui.py tests/cases/test13_large_grid.txt AS
```

1. Select a **Problem file**, or use **Browse...** for another input.
2. Select a **Search method**, then click **Run**.
3. Use **Play** to replay expansions or **Step** to advance one expansion.
4. Use **Back**, **Reset**, and the speed control to inspect the replay.
5. Click **Show result** to highlight the final route immediately.

For AS on case 13, the expected route is
`1 -> 6 -> 7 -> 12 -> 13 -> 18 -> 19 -> 24 -> 25`, with cost **17**.
The expansion log records actual search expansions; it is different from
the count of all created search nodes. Visit-all runs also show which
destinations have been visited at each recorded expansion.

The GUI computes the search before replaying it. A large search can take
time; after 100,000 recorded expansions it stops tracing and suggests using
the CLI. This animation limit does not apply to `search.py` and does not
mean that the graph has no solution. For a Tkinter installation check, run
`python -m tkinter`.

## Visit all destinations research

The `ALL` method finds a lowest-cost route visiting **every** destination.
It uses A* on `(location, visited destinations)` states, with a scaled
nearest-destination plus minimum-spanning-tree heuristic by default.
A location may legitimately be visited more than once.

```text
python search.py tests/cases/test01_spec_example.txt ALL
python search.py tests/visit_all_cases/all01_dead_end.txt ALL
python gui.py tests/visit_all_cases/all01_dead_end.txt ALL
```

The required methods are also available on the visit-all state space:

```text
python search.py tests/visit_all_cases/all01_dead_end.txt BFS-ALL
python search.py tests/visit_all_cases/all01_dead_end.txt CUS1-ALL
python search.py tests/visit_all_cases/all01_dead_end.txt CUS2-ALL
```

`DFS-ALL`, `GBFS-ALL` and `AS-ALL` are also supported. `BFS-ALL`,
`CUS1-ALL` and `CUS2-ALL` target fewest moves; `AS-ALL` and `ALL` target
lowest cost. DFS/GBFS variants do not guarantee an optimum. The second
output line identifies the final destination reached, and the route can
repeat locations. These methods can be selected in the GUI as well.

The wrapper for the `-ALL` methods constructs reachable augmented states
before searching. Up to `V * 2^k` states are possible for V locations and k
destinations, so this can consume substantial time and memory. Its reported
search-node count excludes wrapper preparation and output-path conversion.
The GUI trace cap does not bound that preprocessing work.

Run the dedicated research experiments with:

```text
python research_visit_all.py
```

This writes `results/visit_all.md` and `results/visit_all.json`, comparing
MST, farthest-destination and zero heuristics, simpler baseline approaches,
and growth as destinations are added. Research timings use five runs per
measurement; the required-method benchmark uses thirty.

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
| `route_finding/algorithms/cus1.py` | IDDFS | implemented and tested |
| `route_finding/algorithms/cus2.py` | IDA* for fewest moves | implemented and tested |
| `tests/cases/` | Problem files (need **at least 15**), described in `tests/cases/README.md` | 15 – done |
| `route_finding/trace.py` | Records real node expansions for the GUI replay | done |
| `gui.py` | Tkinter viewer that animates any method on a problem file | done, checked on cases 01 and 13 |
| `route_finding/algorithms/visit_all.py` | Research: cheapest route visiting ALL destinations (`python search.py <file> ALL`) | done |
| `route_finding/algorithms/visit_all_methods.py` | Research: `DFS-ALL` ... `CUS2-ALL`, each required method run unchanged on a (location, visited set) problem | done, tests in `tests/test_visit_all_methods.py` |
| `research_visit_all.py` | Research experiments; writes `results/visit_all.md` | done |
| `tests/visit_all_cases/` | Test maps for the research extension | done |
| `run_tests.py` | Batch runner / results table | done |
| `benchmark_report.py` | Verifies all 90 runs against reference answers and times them | done |
| `tests/` | 92 unit tests (`python -m unittest discover tests`) | passed on 25 October 2026 |
| `tests/cases/expected_results.json` | Locked goal / number_of_nodes / path for all 90 runs | update only after reviewing an intentional output change |

Each algorithm takes a `RouteProblem` and returns `SearchResult(goal_node_or_None, nodes_created)`.
CUS1 is IDDFS; CUS2 is IDA* for fewest moves.

## Design decisions to document in the report

- **Tie-breaking (NOTE 2):** children are generated in ascending node id; `PriorityFrontier` breaks
  equal priorities by insertion order (priorities are rounded to 9 decimal places so floating-point
  noise does not break a genuine tie).
- **Cycles (six required methods):** BFS keeps a global reached set. The other five reject a child already on the
  current path (`node.on_path()`), so a state can still be reached along different branches.
- **number_of_nodes:** every `Node` created, including the root, children rejected as cycles or
  duplicates, and (for CUS1/CUS2) nodes regenerated in later iterations.
- **Goal test timing:** BFS on generation; DFS, GBFS and AS on removal from the frontier; CUS1 when a
  node is first visited; CUS2 when a child is within the current threshold.
- **Heuristic:** straight-line distance to the nearest destination. GBFS uses it directly; AS scales
  it so it never overestimates cost; CUS2 divides it by the longest edge to estimate moves.

## Deliverables checklist

- [x] All 6 methods working (10 marks each)
- [x] ≥ 15 test cases covering different scenarios, results documented in `results/` (10)
- [ ] Report, 8–10 pages excl. cover/TOC, named `<TeamID>.pdf` (20)
  - cover page with names, IDs, signatures, contribution statement · TOC · instructions · introduction ·
    features/bugs/missing · testing · insights (with data) · research · conclusion ·
    acknowledgements/resources (incl. AI use) · references · captioned figures/tables · page numbers
- [x] Research component: visit ALL destinations via the cheapest route (`ALL`; describe the experiments and findings in the report) (10)
- [x] Clean, commented code (up to −10 otherwise)
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

## CUS1: iterative deepening depth-first search

CUS1 is IDDFS: run ascending depth limits starting at zero. Each pass uses
ascending-child DFS with ancestor cycle checks. A boundary is a cutoff only
if it has a successor outside the current path. Stop when a pass has no
cutoff, or after the maximum simple-path depth V-1. Unreachable graphs
therefore terminate. Iterator frames avoid Python recursion.

IDDFS minimizes moves, not travel cost. Every constructed Node counts,
including each pass's root, regenerated children and rejected cycles.
Boundary checks inspect successor labels without constructing child Nodes.
On the supplied example the result is 2 1 4, cost 10, with 8 created nodes.

## CUS2: iterative deepening A star

CUS2 is IDA* for fewest moves. Its f value is depth plus straight-line
distance to the nearest destination divided by the longest geometric edge.
Use zero when no positive-length edge exists. The initial threshold is h at
the origin; the next is the smallest f exceeding the previous threshold.
A pass with no exceeded threshold and no goal means the search is exhausted.

Each pass uses ascending-child DFS with path cycle checks and iterator
frames, not a priority queue. Test a goal only after its f fits the threshold.
Count every constructed Node across all passes, including repeated roots,
threshold rejections and cycle rejections. Costs are recorded, not optimized.
On the supplied example the result is 2 1 4, cost 10, with 23 created nodes.

Both custom methods may repeat substantial work on large graphs. BFS uses a
global reached set while these methods use path checks; comparisons describe
these actual implementations. Tests cover minimum moves, counting actual
Node constructions, repeated passes, unreachable cycles, threshold jumps,
and an IDA* path longer than Python's usual recursion limit.

## Reproducible report evidence

Run `python benchmark_report.py` to validate all 90 method/case combinations
and write `results/comparison.md` and `results/benchmark.json`. It checks
reachability and route validity for every method, minimum cost for AS,
and minimum moves for BFS/CUS1/CUS2 using independent reference calculations.
Timing is the median of 30 runs after a warm-up, excluding input parsing.
The Markdown summary records interpretation limits and selected comparisons.

The earlier Word report draft predates the IDDFS/IDA* replacements. Its custom-method descriptions and measured comparisons need revision before submission.

## Keeping test and report evidence consistent

The full suite passed **92 tests on 25 October 2026**. The standard-case
regression test locks the goal, node count and path for all 90 runs in
`tests/cases/expected_results.json`. A change to these outputs should be
investigated before updating the baseline. For an intentional, verified
change, run `python tests/update_expected_results.py`, rerun the tests,
and regenerate affected report results.

`python benchmark_report.py` writes the required-method results to
`results/benchmark.json` and `results/comparison.md`. Re-running it changes
timing measurements; use one identified measurement run consistently in
the report. The full suite also checks visit-all and tracing behaviour.
Automated checks do not replace visual inspection of the GUI screenshots.

Optional report charts can be generated with
`python research/make_report_charts.py` after their input evidence exists.
This chart script needs Matplotlib (`python -m pip install matplotlib`);
Matplotlib is not required for search.py, gui.py or the unit tests.

Before submission, ensure the report describes IDDFS/IDA*, the implemented
visit-all extension and the current test count. Statements that the
visit-all feature is only proposed are now outdated. Complete the actual
team details, contributions, signatures and AI-use acknowledgement.
