"""Custom search 2 (CUS2) - an informed method to find a shortest path (least moves)."""

from ..node import Node, SearchResult, expand


def cus2(problem):
    """Run CUS2 on `problem` and return a SearchResult.

    Self-learning method. "Shortest" here means fewest moves (edges), not
    lowest cost. Suggested options (pick one and justify it):
      * A* where g(n) = node.depth and h(n) is an estimate of remaining moves
        (e.g. straight-line distance / longest edge length, kept admissible).
      * IDA* (iterative deepening A*) on the same f(n).
      * Weighted A* / beam search (note: these trade optimality for speed).
    """
    root = Node(problem.origin)
    nodes_created = 1

    # TODO: implement
    raise NotImplementedError("CUS2 is not implemented yet")
