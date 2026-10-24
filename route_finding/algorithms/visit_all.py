"""Research extension (ALL): the cheapest route that visits EVERY destination.

The six required methods stop at the first destination they reach. Here the
robot must visit all of them, in whatever order is cheapest, and may pass
through the same location more than once to do so.

Why the ordinary methods cannot simply be reused:

* The goal depends on where the robot has BEEN, not only where it is. The
  search state is therefore (location, set of destinations visited so far).
  Standing at node 3 having visited {4} is a different situation from
  standing at node 3 having visited {4, 5}.
* The best route may revisit a location (for example, backing out of a dead
  end that holds a destination). The required methods reject any location
  already on the current route, which would wrongly discard such routes.
  Here a repeat is rejected only when the same (location, visited set) state
  has already been reached at equal or lower cost.

The search is A* over these states, with the goal tested when a state is
removed from the queue. The visited set is a bit mask (one bit per
destination), so each state is a small (int, int) pair.

Heuristics (all scaled by astar.heuristic_scale so they stay safe when an
edge costs less than its straight-line length):

* "mst" (default): straight-line distance to the NEAREST unvisited
  destination, plus the length of a minimum spanning tree joining all the
  unvisited destinations. Any route that visits them all must first reach
  one of them, then travel a path through the rest, and such a path is at
  least as long as their minimum spanning tree. So it never overestimates.
  The tree depends only on the visited set, so it is computed once per set.
* "farthest": straight-line distance to the farthest unvisited destination.
  Also never overestimates, but much weaker.
* "none": no estimate, i.e. uniform-cost search over the same states.

An estimate that never overestimates is enough for the first all-visited
state removed from the queue to be optimal here, because a state is queued
again whenever a cheaper route to it is found.
"""

from math import inf

from ..frontier import PriorityFrontier
from ..node import Node, SearchResult, expand
from .astar import heuristic_scale

HEURISTICS = ("mst", "farthest", "none")


def _mst_length(points, distance):
    """Total length of a minimum spanning tree over `points` (Prim's algorithm)."""
    if len(points) < 2:
        return 0.0
    best = {p: distance(points[0], p) for p in points[1:]}
    total = 0.0
    while best:
        nearest = min(best, key=best.get)
        total += best.pop(nearest)
        for p in best:
            best[p] = min(best[p], distance(nearest, p))
    return total


def visit_all(problem, heuristic="mst"):
    """Return the cheapest route from the origin that visits every destination.

    result.goal is the final node of the route (the last new destination
    reached); result.goal.path() is the whole route, which may repeat
    locations. nodes_created counts every Node created, as for the other
    methods. `heuristic` is one of HEURISTICS (see the module docstring).
    """
    if heuristic not in HEURISTICS:
        raise ValueError(f"heuristic must be one of {HEURISTICS}")
    goals = sorted(problem.destinations)
    bit = {goal: 1 << i for i, goal in enumerate(goals)}
    all_visited = (1 << len(goals)) - 1
    scale = heuristic_scale(problem)
    tree_length = {}                 # visited mask -> MST length of unvisited goals

    def estimate(location, visited):
        """Safe lower bound on the cost still needed to visit the rest."""
        remaining = [g for g in goals if not visited & bit[g]]
        if heuristic == "none" or not remaining:
            return 0
        to_goals = [problem.distance(location, g) for g in remaining]
        if heuristic == "farthest":
            return scale * max(to_goals)
        if visited not in tree_length:
            tree_length[visited] = _mst_length(remaining, problem.distance)
        return scale * (min(to_goals) + tree_length[visited])

    root = Node(problem.origin)
    nodes_created = 1
    start = (root.state, bit.get(root.state, 0))
    best_cost = {start: 0}          # cheapest known cost of each state
    frontier = PriorityFrontier()
    frontier.push((root, start[1]), estimate(*start))

    while frontier:
        node, visited = frontier.pop()
        # Goal test on removal, as in AS, so the route returned is cheapest.
        if visited == all_visited:
            return SearchResult(node, nodes_created)
        # A cheaper route to this state was found after this one was queued.
        if node.path_cost > best_cost[(node.state, visited)]:
            continue

        for child in expand(problem, node):   # ascending (NOTE 2)
            nodes_created += 1
            state = child.state
            child_visited = visited | bit.get(state, 0)
            key = (state, child_visited)
            # Keep a repeat only if it reaches this state more cheaply.
            if child.path_cost >= best_cost.get(key, inf):
                continue
            best_cost[key] = child.path_cost
            frontier.push((child, child_visited),
                          child.path_cost + estimate(state, child_visited))

    return SearchResult(None, nodes_created)
