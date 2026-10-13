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
| `route_finding/algorithms/dfs.py` | Depth-first search | **TODO** |
| `route_finding/algorithms/bfs.py` | Breadth-first search | **TODO** |
| `route_finding/algorithms/gbfs.py` | Greedy best-first search | **TODO** |
| `route_finding/algorithms/astar.py` | A* search | **TODO** |
| `route_finding/algorithms/cus1.py` | Custom uninformed search | **TODO** |
| `route_finding/algorithms/cus2.py` | Custom informed search (fewest moves) | **TODO** |
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
