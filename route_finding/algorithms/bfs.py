"""Breadth-first search (BFS) - uninformed."""

from ..node import Node, SearchResult, expand


def bfs(problem):
    """Run BFS on `problem` and return a SearchResult.

    Expand all options one level at a time.

    Hints:
      * Frontier is a FIFO queue (collections.deque). Children are added in
        ascending order, which gives the required tie-breaking for free.
      * Decide whether to goal-test when a node is generated or when it is
        expanded - it changes number_of_nodes. Be consistent across methods.
    """
    root = Node(problem.origin)
    nodes_created = 1

    # TODO: implement
    raise NotImplementedError("BFS is not implemented yet")
