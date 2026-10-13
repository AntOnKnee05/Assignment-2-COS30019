"""Registry of search methods, keyed by the method name used on the command line."""

from .astar import astar
from .bfs import bfs
from .cus1 import cus1
from .cus2 import cus2
from .dfs import dfs
from .gbfs import gbfs

METHODS = {
    "DFS": dfs,
    "BFS": bfs,
    "GBFS": gbfs,
    "AS": astar,
    "CUS1": cus1,
    "CUS2": cus2,
}
