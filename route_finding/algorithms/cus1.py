"""Custom search 1 (CUS1) - an uninformed method to reach the goal."""

from ..node import Node, SearchResult, expand


def cus1(problem):
    """Run CUS1 on `problem` and return a SearchResult.

    Self-learning method. Suggested options (pick one and justify it):
      * Uniform-cost search (priority = g(n)) - optimal on cost, no heuristic.
      * Iterative deepening DFS (IDDFS) - BFS-like completeness, DFS memory.
      * Depth-limited search / bidirectional search.
    """
    root = Node(problem.origin)
    nodes_created = 1

    # TODO: implement
    raise NotImplementedError("CUS1 is not implemented yet")
