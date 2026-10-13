"""A* search (AS) - informed."""

from ..node import Node, SearchResult, expand


def astar(problem):
    """Run A* on `problem` and return a SearchResult.

    Evaluate nodes with f(n) = g(n) + h(n), where g(n) = node.path_cost.

    Hints:
      * Use frontier.PriorityFrontier with priority = node.path_cost + h(n).
      * Goal-test when a node is POPPED, not when it is generated, otherwise
        the path returned may not be optimal.
    """
    root = Node(problem.origin)
    nodes_created = 1

    # TODO: implement
    raise NotImplementedError("AS is not implemented yet")
