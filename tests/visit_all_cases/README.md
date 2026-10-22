# Visit-all-destinations test maps (research extension)

Run any of them with `python search.py tests/visit_all_cases/<file> ALL`.
`tests/test_visit_all.py` checks every result against a brute-force answer.

| File | What it tests | Cheapest route visiting all |
|---|---|---|
| `all01_dead_end.txt` | Destination 3 is a dead end; the route must come back through node 2 | 1 2 3 2 4 5 (cost 10) |
| `all02_greedy_trap.txt` | Visiting the nearest destination first is not optimal | 3 2 1 2 3 4 5 6 (cost 7); nearest-first costs 8 |
| `all03_unreachable.txt` | Destination 4 cannot be reached, so there is no solution | none |
| `all04_origin_is_destination.txt` | The origin counts as visited at the start | 1 2 3 (cost 2) |
| `all05_grid_five_destinations.txt` | 6 x 6 grid, five destinations; used to measure search effort | see `results/visit_all.md` |
