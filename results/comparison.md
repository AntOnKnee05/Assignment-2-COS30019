# Search comparison evidence

All 90 method/case combinations passed independent correctness checks.
A missing route is a correct outcome for the deliberately unreachable case.

## Measurement method

- Timing: median of 30 runs after one warm-up; input parsing excluded.
- Nodes: every created search Node, including root and rejected children; IDDFS/IDA* include regenerated roots and children across all iterations.
- Cost: sum of directed edge costs; moves: number of edges in the route.
- Reachability, route edges and reported costs checked for all methods.
- Bellman-Ford reference checks minimum cost for AS and minimum moves for BFS/CUS1/CUS2.
- BFS uses global duplicate suppression and goal tests on generation; other methods use path cycle checks; custom methods use depth-first iterations within limits.
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
| CUS1 | 2 -> 1 -> 4 | 10 | 2 | 8 |
| CUS2 | 2 -> 1 -> 4 | 10 | 2 | 23 |

## Useful findings for the report

- Cheap-long versus expensive-short: compare BFS/CUS1/CUS2 with AS to explain moves versus cost.
- Greedy trap: GBFS chooses a route costing 34; a cheapest route costs 18.
- Misleading geometry: scaled A* still finds cost 2 despite raw Euclidean distance overestimating.
- Grid: compare IDDFS and IDA* counts to discuss repeated work and heuristic guidance; they target moves, unlike AS.
- Unreachable case: all methods must return no route; that is not an algorithm failure.
- Original BFS example count was 4; corrected count is 5 because a generated duplicate also creates a Node.

## Complete measured results

| Case | Method | Outcome | Cost | Moves | Nodes | Median ms |
|---|---|---|---:|---:|---:|---:|
| test01_spec_example.txt | DFS | route found | 15 | 3 | 9 | 0.0066 |
| test01_spec_example.txt | BFS | route found | 10 | 2 | 5 | 0.0036 |
| test01_spec_example.txt | GBFS | route found | 10 | 2 | 7 | 0.0134 |
| test01_spec_example.txt | AS | route found | 10 | 2 | 9 | 0.0239 |
| test01_spec_example.txt | CUS1 | route found | 10 | 2 | 8 | 0.0100 |
| test01_spec_example.txt | CUS2 | route found | 10 | 2 | 23 | 0.0466 |
| test02_origin_is_goal.txt | DFS | route found | 0 | 0 | 1 | 0.0007 |
| test02_origin_is_goal.txt | BFS | route found | 0 | 0 | 1 | 0.0006 |
| test02_origin_is_goal.txt | GBFS | route found | 0 | 0 | 1 | 0.0023 |
| test02_origin_is_goal.txt | AS | route found | 0 | 0 | 1 | 0.0031 |
| test02_origin_is_goal.txt | CUS1 | route found | 0 | 0 | 1 | 0.0011 |
| test02_origin_is_goal.txt | CUS2 | route found | 0 | 0 | 1 | 0.0029 |
| test03_unreachable.txt | DFS | correctly unreachable | N/A | N/A | 3 | 0.0028 |
| test03_unreachable.txt | BFS | correctly unreachable | N/A | N/A | 3 | 0.0025 |
| test03_unreachable.txt | GBFS | correctly unreachable | N/A | N/A | 3 | 0.0051 |
| test03_unreachable.txt | AS | correctly unreachable | N/A | N/A | 3 | 0.0066 |
| test03_unreachable.txt | CUS1 | correctly unreachable | N/A | N/A | 3 | 0.0043 |
| test03_unreachable.txt | CUS2 | correctly unreachable | N/A | N/A | 5 | 0.0092 |
| test04_one_way_edge.txt | DFS | route found | 11 | 2 | 3 | 0.0031 |
| test04_one_way_edge.txt | BFS | route found | 11 | 2 | 3 | 0.0026 |
| test04_one_way_edge.txt | GBFS | route found | 11 | 2 | 3 | 0.0063 |
| test04_one_way_edge.txt | AS | route found | 11 | 2 | 3 | 0.0084 |
| test04_one_way_edge.txt | CUS1 | route found | 11 | 2 | 6 | 0.0067 |
| test04_one_way_edge.txt | CUS2 | route found | 11 | 2 | 8 | 0.0149 |
| test05_tie_break_ascending.txt | DFS | route found | 2 | 2 | 4 | 0.0034 |
| test05_tie_break_ascending.txt | BFS | route found | 2 | 2 | 4 | 0.0032 |
| test05_tie_break_ascending.txt | GBFS | route found | 2 | 2 | 4 | 0.0082 |
| test05_tie_break_ascending.txt | AS | route found | 2 | 2 | 5 | 0.0124 |
| test05_tie_break_ascending.txt | CUS1 | route found | 2 | 2 | 7 | 0.0079 |
| test05_tie_break_ascending.txt | CUS2 | route found | 2 | 2 | 6 | 0.0121 |
| test06_cheap_long_vs_short_expensive.txt | DFS | route found | 3 | 3 | 5 | 0.0044 |
| test06_cheap_long_vs_short_expensive.txt | BFS | route found | 40 | 2 | 5 | 0.0038 |
| test06_cheap_long_vs_short_expensive.txt | GBFS | route found | 40 | 2 | 4 | 0.0079 |
| test06_cheap_long_vs_short_expensive.txt | AS | route found | 3 | 3 | 5 | 0.0129 |
| test06_cheap_long_vs_short_expensive.txt | CUS1 | route found | 40 | 2 | 9 | 0.0106 |
| test06_cheap_long_vs_short_expensive.txt | CUS2 | route found | 40 | 2 | 17 | 0.0307 |
| test07_multiple_destinations.txt | DFS | route found | 5 | 1 | 4 | 0.0026 |
| test07_multiple_destinations.txt | BFS | route found | 5 | 1 | 2 | 0.0019 |
| test07_multiple_destinations.txt | GBFS | route found | 5 | 1 | 4 | 0.0083 |
| test07_multiple_destinations.txt | AS | route found | 4 | 2 | 5 | 0.0133 |
| test07_multiple_destinations.txt | CUS1 | route found | 5 | 1 | 3 | 0.0033 |
| test07_multiple_destinations.txt | CUS2 | route found | 5 | 1 | 2 | 0.0066 |
| test08_cycle_trap.txt | DFS | route found | 7 | 3 | 7 | 0.0061 |
| test08_cycle_trap.txt | BFS | route found | 7 | 3 | 6 | 0.0041 |
| test08_cycle_trap.txt | GBFS | route found | 7 | 3 | 6 | 0.0105 |
| test08_cycle_trap.txt | AS | route found | 7 | 3 | 6 | 0.0137 |
| test08_cycle_trap.txt | CUS1 | route found | 7 | 3 | 13 | 0.0141 |
| test08_cycle_trap.txt | CUS2 | route found | 7 | 3 | 12 | 0.0207 |
| test09_dfs_deep_branch.txt | DFS | route found | 9 | 8 | 10 | 0.0105 |
| test09_dfs_deep_branch.txt | BFS | route found | 3 | 1 | 3 | 0.0024 |
| test09_dfs_deep_branch.txt | GBFS | route found | 3 | 1 | 3 | 0.0059 |
| test09_dfs_deep_branch.txt | AS | route found | 3 | 1 | 3 | 0.0102 |
| test09_dfs_deep_branch.txt | CUS1 | route found | 3 | 1 | 4 | 0.0047 |
| test09_dfs_deep_branch.txt | CUS2 | route found | 3 | 1 | 3 | 0.0095 |
| test10_greedy_trap.txt | DFS | route found | 34 | 2 | 4 | 0.0033 |
| test10_greedy_trap.txt | BFS | route found | 34 | 2 | 4 | 0.0032 |
| test10_greedy_trap.txt | GBFS | route found | 34 | 2 | 4 | 0.0081 |
| test10_greedy_trap.txt | AS | route found | 18 | 3 | 6 | 0.0152 |
| test10_greedy_trap.txt | CUS1 | route found | 34 | 2 | 7 | 0.0080 |
| test10_greedy_trap.txt | CUS2 | route found | 34 | 2 | 10 | 0.0190 |
| test11_inadmissible_heuristic.txt | DFS | route found | 2 | 2 | 4 | 0.0034 |
| test11_inadmissible_heuristic.txt | BFS | route found | 12 | 1 | 3 | 0.0024 |
| test11_inadmissible_heuristic.txt | GBFS | route found | 12 | 1 | 3 | 0.0059 |
| test11_inadmissible_heuristic.txt | AS | route found | 2 | 2 | 4 | 0.0099 |
| test11_inadmissible_heuristic.txt | CUS1 | route found | 12 | 1 | 4 | 0.0047 |
| test11_inadmissible_heuristic.txt | CUS2 | route found | 12 | 1 | 6 | 0.0117 |
| test12_dead_ends.txt | DFS | route found | 6 | 3 | 9 | 0.0094 |
| test12_dead_ends.txt | BFS | route found | 6 | 3 | 9 | 0.0068 |
| test12_dead_ends.txt | GBFS | route found | 6 | 3 | 6 | 0.0115 |
| test12_dead_ends.txt | AS | route found | 6 | 3 | 7 | 0.0191 |
| test12_dead_ends.txt | CUS1 | route found | 6 | 3 | 22 | 0.0254 |
| test12_dead_ends.txt | CUS2 | route found | 6 | 3 | 29 | 0.0534 |
| test13_large_grid.txt | DFS | route found | 78 | 24 | 79 | 0.0713 |
| test13_large_grid.txt | BFS | route found | 40 | 8 | 76 | 0.0338 |
| test13_large_grid.txt | GBFS | route found | 25 | 8 | 29 | 0.0460 |
| test13_large_grid.txt | AS | route found | 17 | 8 | 299 | 0.5156 |
| test13_large_grid.txt | CUS1 | route found | 40 | 8 | 1421 | 1.7868 |
| test13_large_grid.txt | CUS2 | route found | 40 | 8 | 833 | 1.3102 |
| test14_decimal_values.txt | DFS | route found | 4.4 | 2 | 4 | 0.0037 |
| test14_decimal_values.txt | BFS | route found | 4.4 | 2 | 4 | 0.0036 |
| test14_decimal_values.txt | GBFS | route found | 4.4 | 2 | 4 | 0.0087 |
| test14_decimal_values.txt | AS | route found | 4.4 | 2 | 4 | 0.0113 |
| test14_decimal_values.txt | CUS1 | route found | 4.4 | 2 | 7 | 0.0084 |
| test14_decimal_values.txt | CUS2 | route found | 4.4 | 2 | 15 | 0.0288 |
| test15_equal_cost_tie.txt | DFS | route found | 4 | 2 | 4 | 0.0036 |
| test15_equal_cost_tie.txt | BFS | route found | 4 | 2 | 4 | 0.0033 |
| test15_equal_cost_tie.txt | GBFS | route found | 4 | 2 | 4 | 0.0093 |
| test15_equal_cost_tie.txt | AS | route found | 4 | 2 | 5 | 0.0143 |
| test15_equal_cost_tie.txt | CUS1 | route found | 4 | 2 | 7 | 0.0082 |
| test15_equal_cost_tie.txt | CUS2 | route found | 4 | 2 | 3 | 0.0090 |

## Remaining submission work

- Write the 8-10 page report with actual team details, contributions and AI-use acknowledgement.
- Add properly sourced algorithm explanations and references.
- Decide and document the research component; do not claim GUI validation or memory experiments that were not performed.
- Confirm tie-breaking interpretation and choice of custom methods with course guidance.
- Complete team signatures and required tutor progress records.
