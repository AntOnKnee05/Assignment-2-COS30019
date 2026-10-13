"""Greedy best-first search (GBFS) - informed."""

from ..node import Node, SearchResult, expand


def gbfs(problem):
    """Run GBFS on `problem` and return a SearchResult.

    Evaluate nodes using only h(n): problem.heuristic(state).

    Hints:
      * Use frontier.PriorityFrontier with priority = h(n).
      * Needs cycle checking, like DFS.
    """
    root = Node(problem.origin)
    nodes_created = 1

    # TODO: implement
    raise NotImplementedError("GBFS is not implemented yet")
