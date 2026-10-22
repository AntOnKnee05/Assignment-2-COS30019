"""Registry of search methods, keyed by the method name used on the command line."""

from .astar import astar
from .bfs import bfs
from .cus1 import cus1
from .cus2 import cus2
from .dfs import dfs
from .gbfs import gbfs
from .visit_all import visit_all

METHODS = {
    "DFS": dfs,
    "BFS": bfs,
    "GBFS": gbfs,
    "AS": astar,
    "CUS1": cus1,
    "CUS2": cus2,
}

# Research extension, kept separate so the six required methods (and the
# tests and report figures built on them) are unaffected. search.py accepts
# both: python search.py <filename> ALL
RESEARCH_METHODS = {
    "ALL": visit_all,   # cheapest route visiting every destination
}
