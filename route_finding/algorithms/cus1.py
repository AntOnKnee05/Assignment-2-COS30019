"""CUS1: uniform-cost tree search, an uninformed minimum-cost method."""

from ..node import Node, SearchResult, expand
from ..frontier import PriorityFrontier


def cus1(problem):
    """Explore the lowest accumulated cost first, without a heuristic.

    Assumes finite, nonnegative edge costs. Path cycle checking prevents
    loops while allowing alternative routes to the same state. Count every
    created Node, including the root and children rejected as cycles.
    """
    root = Node(problem.origin)
    nodes_created = 1
    frontier = PriorityFrontier()
    frontier.push(root, 0)

    while frontier:
        node = frontier.pop()
        # Wait until removal: a cheaper goal route may still be waiting.
        if problem.is_goal(node.state):
            return SearchResult(node, nodes_created)

        for child in expand(problem, node):
            nodes_created += 1
            if not node.on_path(child.state):
                frontier.push(child, child.path_cost)

    return SearchResult(None, nodes_created)
