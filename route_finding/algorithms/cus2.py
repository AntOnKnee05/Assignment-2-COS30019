"""CUS2: A* on move count, with a geometric lower bound on moves left."""

from ..node import Node, SearchResult, expand
from ..frontier import PriorityFrontier


def longest_edge_length(problem):
    """One move can cover at most this much straight-line distance."""
    return max((problem.distance(source, target)
                for source in problem.nodes
                for target, _ in problem.successors(source)), default=0.0)


def cus2(problem):
    """Minimize moves using f = depth + distance / longest edge length.

    By the triangle inequality, k moves can cover at most k * longest_edge
    distance. The estimate therefore never exceeds the moves required.
    Use zero when every edge has zero length (or there are no edges).
    Path costs are still recorded for reporting, but do not affect priority.
    """
    longest = longest_edge_length(problem)

    def remaining_moves(state):
        return problem.heuristic(state) / longest if longest > 0 else 0.0

    root = Node(problem.origin)
    nodes_created = 1
    frontier = PriorityFrontier()
    frontier.push(root, remaining_moves(root.state))

    while frontier:
        node = frontier.pop()
        if problem.is_goal(node.state):
            return SearchResult(node, nodes_created)

        for child in expand(problem, node):
            # Count even children rejected because they repeat an ancestor.
            nodes_created += 1
            if not node.on_path(child.state):
                frontier.push(child, child.depth + remaining_moves(child.state))

    return SearchResult(None, nodes_created)
