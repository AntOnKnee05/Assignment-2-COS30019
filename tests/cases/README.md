# Test cases

Each file uses the assignment's problem format. Run them all with `python run_tests.py`,
or watch one with `python gui.py tests/cases/<file> <method>`.

**Cheapest path** is the minimum-cost route, which AS must find. **Fewest moves** is the
minimum-edge route, which BFS, CUS1 and CUS2 must find. Both columns were checked
independently (Bellman-Ford for cost, a plain breadth-first traversal for moves) in
`tests/helpers.py`. **h admissible** says whether every edge costs at least its straight-line
length, i.e. whether *raw* straight-line distance is a safe cost estimate. AS does not rely on
this: it scales the estimate down when needed (see `astar.heuristic_scale`).

`expected_results.json` records the exact goal, number_of_nodes and path for every method on
every case; `tests/test_regression.py` fails if any of them change.

| # | File | Scenario it tests | Cheapest path (cost) | Fewest moves | h admissible |
|---|---|---|---|---|---|
| 1 | `test01_spec_example.txt` | Example from the assignment spec | 2 1 4 (10) | 2 1 4 | yes |
| 2 | `test02_origin_is_goal.txt` | Origin is already a destination; should stop with 1 node | 1 (0) | 1 | yes |
| 3 | `test03_unreachable.txt` | Destination has no incoming path; must report no solution and terminate | none | none | yes |
| 4 | `test04_one_way_edge.txt` | Directed edges: 1→2 doesn't exist, so the route must go around | 1 3 2 (11) | 1 3 2 | no |
| 5 | `test05_tie_break_ascending.txt` | Equal options; smaller node id must be expanded first (NOTE 2) | 1 2 4 (2) | 1 2 4 | no |
| 6 | `test06_cheap_long_vs_short_expensive.txt` | Fewest moves ≠ cheapest: BFS should differ from A* | 1 2 3 4 (3) | 1 5 4 (cost 40) | yes |
| 7 | `test07_multiple_destinations.txt` | Two destinations; the nearest by cost isn't the nearest by moves | 1 4 3 (4) | 1 2 (cost 5) | no |
| 8 | `test08_cycle_trap.txt` | Cycle 1→2→3→4→1 that the lowest-id-first order walks into; tests cycle handling (DFS can loop forever without it) | 1 2 3 5 (7) | 1 2 3 5 | yes |
| 9 | `test09_dfs_deep_branch.txt` | Lowest-id branch is a long 8-edge detour; DFS should find a long, expensive path while BFS/A* take the direct edge | 1 9 (3) | 1 9 | yes |
| 10 | `test10_greedy_trap.txt` | Node closest to the goal leads to a very expensive edge; GBFS should be fooled (cost 34), A* should not | 1 3 4 5 (18) | 1 2 5 (cost 34) | yes |
| 11 | `test11_inadmissible_heuristic.txt` | A "tunnel" whose edges cost less than their straight-line length; A* with straight-line h can return the cost 12 route instead of the optimal 2 | 1 2 3 (2) | 1 3 (cost 12) | **no** |
| 12 | `test12_dead_ends.txt` | Several dead-end branches to back out of, plus an isolated node (10) with no edges | 1 4 8 9 (6) | 1 4 8 9 | yes |
| 13 | `test13_large_grid.txt` | 5×5 grid, 25 nodes, 80 directed edges; slow roads round the edge and fast roads through the middle. Good for comparing nodes created and time | 1 6 7 12 13 18 19 24 25 (17) | 1 2 3 4 5 10 15 20 25 (cost 40) | yes |
| 14 | `test14_decimal_values.txt` | Decimal coordinates and edge costs | 1 2 4 (4.4) | 1 2 4 | yes |
| 15 | `test15_equal_cost_tie.txt` | Two destinations at exactly the same cost and depth; the tie-breaking rule decides which is returned | 1 5 2 or 1 4 3 (4) | 1 4 3 | yes |

Notes:

- Case 15 has two equally good answers (1 5 2 and 1 4 3, both cost 4 in two moves). Ties are
  broken by insertion order with siblings added in ascending id order (NOTE 2), so node 4 is
  handled before node 5 and every method returns 1 4 3.
- Cases 4, 5, 7 and 11 contain edges that cost less than their straight-line length. Raw
  straight-line distance can therefore overestimate on them; case 11 is built so that A* with
  the raw estimate would return the cost-12 route. The scaled estimate used by AS keeps it
  optimal on all fifteen cases.
- DFS and GBFS do not guarantee either optimum, so their routes aren't listed here; see
  `expected_results.json` or `python run_tests.py`.
