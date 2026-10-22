# Visit-all-destinations research results

Times are the median of 5 runs. Every optimal cost matches the brute-force
reference in tests/test_visit_all.py. Nodes = search nodes created.

## Optimal tour versus simpler approaches

| Case | Dest. | Optimal cost | Revisits | Nearest-first cost | Location-only check | Nodes (mst) | Nodes (farthest) | Nodes (none) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| test01_spec_example.txt | 2 | 17 | 0 | 17 | 17 | 15 | 15 | 25 |
| all01_dead_end.txt | 2 | 10 | 1 | 10 | fails | 8 | 9 | 9 |
| all02_greedy_trap.txt | 3 | 7 | 2 | 8 | fails | 14 | 22 | 34 |
| all05_grid_five_destinations.txt | 5 | 51 | 2 | 55 | 51 | 2,309 | 2,536 | 3,045 |

## Growth with the number of destinations (10 x 10 grid)

| Destinations | Possible states | Optimal cost | Nodes (mst) | Nodes (farthest) | Nodes (none) | ms (mst) | ms (farthest) | ms (none) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 200 | 35 | 359 | 359 | 359 | 0.4 | 0.4 | 0.3 |
| 2 | 400 | 53 | 606 | 606 | 794 | 0.7 | 0.7 | 0.6 |
| 3 | 800 | 62 | 1,208 | 1,414 | 1,841 | 1.3 | 1.6 | 1.3 |
| 4 | 1,600 | 70 | 3,126 | 3,563 | 4,431 | 3.7 | 4.1 | 3.3 |
| 5 | 3,200 | 71 | 5,140 | 6,662 | 8,629 | 6.6 | 8.4 | 6.6 |
| 6 | 6,400 | 73 | 9,635 | 13,284 | 17,140 | 13.7 | 18.1 | 14.1 |
| 7 | 12,800 | 74 | 18,262 | 25,598 | 33,592 | 28.2 | 36.7 | 29.0 |
| 8 | 25,600 | 75 | 35,126 | 50,087 | 65,865 | 56.9 | 77.9 | 60.9 |
| 9 | 51,200 | 76 | 49,238 | 85,924 | 119,011 | 89.7 | 145.6 | 118.3 |
