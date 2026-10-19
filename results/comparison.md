# Search comparison evidence

All 90 method/case combinations passed independent correctness checks.
A missing route is a correct outcome for the deliberately unreachable case.

## Measurement method

- Timing: median of 30 runs after one warm-up; input parsing excluded.
- Nodes: every created search Node, including root and rejected children.
- Cost: sum of directed edge costs; moves: number of edges in the route.
- Reachability, route edges and reported costs checked for all methods.
- Bellman-Ford reference checks minimum cost for AS/CUS1 and minimum moves for BFS/CUS2.
- BFS uses global duplicate suppression and goal tests on generation; other methods use path cycle checks and goal tests on removal.
- These comparisons describe the implemented variants, not isolated algorithm effects.
- Small timings are sensitive to system load; memory usage was not measured.
- Fifteen small cases do not establish general scalability or a universal fastest method.

## Supplied example

| Method | Route | Cost | Moves | Nodes created |
|---|---|---:|---:|---:|
| DFS | 2 -> 1 -> 3 -> 5 | 15 | 3 | 9 |
| BFS | 2 -> 1 -> 4 | 10 | 2 | 5 |
| GBFS | 2 -> 3 -> 5 | 10 | 2 | 7 |
| AS | 2 -> 3 -> 5 | 10 | 2 | 9 |
| CUS1 | 2 -> 1 -> 4 | 10 | 2 | 15 |
| CUS2 | 2 -> 3 -> 5 | 10 | 2 | 9 |

## Useful findings for the report

- Cheap-long versus expensive-short: compare BFS/CUS2 with AS/CUS1 to explain moves versus cost.
- Greedy trap: GBFS chooses a route costing 34; a cheapest route costs 18.
- Misleading geometry: scaled A* still finds cost 2 despite raw Euclidean distance overestimating.
- Grid: compare created-node counts for AS and CUS1 to discuss heuristic guidance.
- Unreachable case: all methods must return no route; that is not an algorithm failure.
- Original BFS example count was 4; corrected count is 5 because a generated duplicate also creates a Node.

## Complete measured results

| Case | Method | Outcome | Cost | Moves | Nodes | Median ms |
|---|---|---|---:|---:|---:|---:|
| test01_spec_example.txt | DFS | route found | 15 | 3 | 9 | 0.0053 |
| test01_spec_example.txt | BFS | route found | 10 | 2 | 5 | 0.0028 |
| test01_spec_example.txt | GBFS | route found | 10 | 2 | 7 | 0.0106 |
| test01_spec_example.txt | AS | route found | 10 | 2 | 9 | 0.0188 |
| test01_spec_example.txt | CUS1 | route found | 10 | 2 | 15 | 0.0100 |
| test01_spec_example.txt | CUS2 | route found | 10 | 2 | 9 | 0.0196 |
| test02_origin_is_goal.txt | DFS | route found | 0 | 0 | 1 | 0.0006 |
| test02_origin_is_goal.txt | BFS | route found | 0 | 0 | 1 | 0.0005 |
| test02_origin_is_goal.txt | GBFS | route found | 0 | 0 | 1 | 0.0018 |
| test02_origin_is_goal.txt | AS | route found | 0 | 0 | 1 | 0.0025 |
| test02_origin_is_goal.txt | CUS1 | route found | 0 | 0 | 1 | 0.0011 |
| test02_origin_is_goal.txt | CUS2 | route found | 0 | 0 | 1 | 0.0029 |
| test03_unreachable.txt | DFS | correctly unreachable | N/A | N/A | 3 | 0.0023 |
| test03_unreachable.txt | BFS | correctly unreachable | N/A | N/A | 3 | 0.0020 |
| test03_unreachable.txt | GBFS | correctly unreachable | N/A | N/A | 3 | 0.0041 |
| test03_unreachable.txt | AS | correctly unreachable | N/A | N/A | 3 | 0.0052 |
| test03_unreachable.txt | CUS1 | correctly unreachable | N/A | N/A | 3 | 0.0026 |
| test03_unreachable.txt | CUS2 | correctly unreachable | N/A | N/A | 3 | 0.0057 |
| test04_one_way_edge.txt | DFS | route found | 11 | 2 | 3 | 0.0025 |
| test04_one_way_edge.txt | BFS | route found | 11 | 2 | 3 | 0.0021 |
| test04_one_way_edge.txt | GBFS | route found | 11 | 2 | 3 | 0.0052 |
| test04_one_way_edge.txt | AS | route found | 11 | 2 | 3 | 0.0066 |
| test04_one_way_edge.txt | CUS1 | route found | 11 | 2 | 3 | 0.0030 |
| test04_one_way_edge.txt | CUS2 | route found | 11 | 2 | 3 | 0.0072 |
| test05_tie_break_ascending.txt | DFS | route found | 2 | 2 | 4 | 0.0027 |
| test05_tie_break_ascending.txt | BFS | route found | 2 | 2 | 4 | 0.0025 |
| test05_tie_break_ascending.txt | GBFS | route found | 2 | 2 | 4 | 0.0064 |
| test05_tie_break_ascending.txt | AS | route found | 2 | 2 | 5 | 0.0101 |
| test05_tie_break_ascending.txt | CUS1 | route found | 2 | 2 | 5 | 0.0045 |
| test05_tie_break_ascending.txt | CUS2 | route found | 2 | 2 | 5 | 0.0107 |
| test06_cheap_long_vs_short_expensive.txt | DFS | route found | 3 | 3 | 5 | 0.0035 |
| test06_cheap_long_vs_short_expensive.txt | BFS | route found | 40 | 2 | 5 | 0.0030 |
| test06_cheap_long_vs_short_expensive.txt | GBFS | route found | 40 | 2 | 4 | 0.0062 |
| test06_cheap_long_vs_short_expensive.txt | AS | route found | 3 | 3 | 5 | 0.0103 |
| test06_cheap_long_vs_short_expensive.txt | CUS1 | route found | 3 | 3 | 5 | 0.0044 |
| test06_cheap_long_vs_short_expensive.txt | CUS2 | route found | 40 | 2 | 5 | 0.0110 |
| test07_multiple_destinations.txt | DFS | route found | 5 | 1 | 4 | 0.0021 |
| test07_multiple_destinations.txt | BFS | route found | 5 | 1 | 2 | 0.0015 |
| test07_multiple_destinations.txt | GBFS | route found | 5 | 1 | 4 | 0.0066 |
| test07_multiple_destinations.txt | AS | route found | 4 | 2 | 5 | 0.0104 |
| test07_multiple_destinations.txt | CUS1 | route found | 4 | 2 | 5 | 0.0039 |
| test07_multiple_destinations.txt | CUS2 | route found | 5 | 1 | 4 | 0.0092 |
| test08_cycle_trap.txt | DFS | route found | 7 | 3 | 7 | 0.0050 |
| test08_cycle_trap.txt | BFS | route found | 7 | 3 | 6 | 0.0034 |
| test08_cycle_trap.txt | GBFS | route found | 7 | 3 | 6 | 0.0083 |
| test08_cycle_trap.txt | AS | route found | 7 | 3 | 6 | 0.0107 |
| test08_cycle_trap.txt | CUS1 | route found | 7 | 3 | 7 | 0.0056 |
| test08_cycle_trap.txt | CUS2 | route found | 7 | 3 | 6 | 0.0114 |
| test09_dfs_deep_branch.txt | DFS | route found | 9 | 8 | 10 | 0.0129 |
| test09_dfs_deep_branch.txt | BFS | route found | 3 | 1 | 3 | 0.0023 |
| test09_dfs_deep_branch.txt | GBFS | route found | 3 | 1 | 3 | 0.0047 |
| test09_dfs_deep_branch.txt | AS | route found | 3 | 1 | 3 | 0.0118 |
| test09_dfs_deep_branch.txt | CUS1 | route found | 3 | 1 | 5 | 0.0045 |
| test09_dfs_deep_branch.txt | CUS2 | route found | 3 | 1 | 3 | 0.0088 |
| test10_greedy_trap.txt | DFS | route found | 34 | 2 | 4 | 0.0027 |
| test10_greedy_trap.txt | BFS | route found | 34 | 2 | 4 | 0.0026 |
| test10_greedy_trap.txt | GBFS | route found | 34 | 2 | 4 | 0.0063 |
| test10_greedy_trap.txt | AS | route found | 18 | 3 | 6 | 0.0119 |
| test10_greedy_trap.txt | CUS1 | route found | 18 | 3 | 6 | 0.0054 |
| test10_greedy_trap.txt | CUS2 | route found | 34 | 2 | 4 | 0.0092 |
| test11_inadmissible_heuristic.txt | DFS | route found | 2 | 2 | 4 | 0.0028 |
| test11_inadmissible_heuristic.txt | BFS | route found | 12 | 1 | 3 | 0.0019 |
| test11_inadmissible_heuristic.txt | GBFS | route found | 12 | 1 | 3 | 0.0046 |
| test11_inadmissible_heuristic.txt | AS | route found | 2 | 2 | 4 | 0.0080 |
| test11_inadmissible_heuristic.txt | CUS1 | route found | 2 | 2 | 4 | 0.0035 |
| test11_inadmissible_heuristic.txt | CUS2 | route found | 12 | 1 | 3 | 0.0069 |
| test12_dead_ends.txt | DFS | route found | 6 | 3 | 9 | 0.0078 |
| test12_dead_ends.txt | BFS | route found | 6 | 3 | 9 | 0.0055 |
| test12_dead_ends.txt | GBFS | route found | 6 | 3 | 6 | 0.0090 |
| test12_dead_ends.txt | AS | route found | 6 | 3 | 7 | 0.0148 |
| test12_dead_ends.txt | CUS1 | route found | 6 | 3 | 9 | 0.0089 |
| test12_dead_ends.txt | CUS2 | route found | 6 | 3 | 7 | 0.0156 |
| test13_large_grid.txt | DFS | route found | 78 | 24 | 79 | 0.0556 |
| test13_large_grid.txt | BFS | route found | 40 | 8 | 76 | 0.0270 |
| test13_large_grid.txt | GBFS | route found | 25 | 8 | 29 | 0.0372 |
| test13_large_grid.txt | AS | route found | 17 | 8 | 299 | 0.4168 |
| test13_large_grid.txt | CUS1 | route found | 17 | 8 | 736 | 0.5617 |
| test13_large_grid.txt | CUS2 | route found | 25 | 8 | 573 | 1.1551 |
| test14_decimal_values.txt | DFS | route found | 4.4 | 2 | 4 | 0.0029 |
| test14_decimal_values.txt | BFS | route found | 4.4 | 2 | 4 | 0.0027 |
| test14_decimal_values.txt | GBFS | route found | 4.4 | 2 | 4 | 0.0068 |
| test14_decimal_values.txt | AS | route found | 4.4 | 2 | 4 | 0.0087 |
| test14_decimal_values.txt | CUS1 | route found | 4.4 | 2 | 5 | 0.0046 |
| test14_decimal_values.txt | CUS2 | route found | 4.4 | 2 | 5 | 0.0111 |
| test15_equal_cost_tie.txt | DFS | route found | 4 | 2 | 4 | 0.0028 |
| test15_equal_cost_tie.txt | BFS | route found | 4 | 2 | 4 | 0.0026 |
| test15_equal_cost_tie.txt | GBFS | route found | 4 | 2 | 4 | 0.0074 |
| test15_equal_cost_tie.txt | AS | route found | 4 | 2 | 5 | 0.0113 |
| test15_equal_cost_tie.txt | CUS1 | route found | 4 | 2 | 5 | 0.0045 |
| test15_equal_cost_tie.txt | CUS2 | route found | 4 | 2 | 5 | 0.0188 |

## Remaining submission work

- Write the 8-10 page report with actual team details, contributions and AI-use acknowledgement.
- Add properly sourced algorithm explanations and references.
- Decide and document the research component; do not claim GUI validation or memory experiments that were not performed.
- Confirm tie-breaking interpretation and choice of custom methods with course guidance.
- Complete team signatures and required tutor progress records.
