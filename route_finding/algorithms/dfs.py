"""Depth-first search (DFS) - uninformed."""

from ..node import Node, SearchResult, expand


def dfs(problem):
    """Run DFS on `problem` and return a SearchResult.

    Select one option, try it, go back when there are no more options.

    Hints:
      * Frontier is a LIFO stack. To expand the smallest node first, push the
        children in DESCENDING order (reverse of expand()) so the smallest is
        on top.
      * The graph has cycles (e.g. 1 <-> 3), so plain tree search can loop
        forever. Avoid it with node.on_path(state) (keeps it tree search) or a
        visited set (graph search) - state which one you chose in the report.
    """
    root = Node(problem.origin)
    nodes_created = 1

    # TODO: implement
    raise NotImplementedError("DFS is not implemented yet")
