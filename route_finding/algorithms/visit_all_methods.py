"""Visit-all versions of the six required methods (DFS-ALL ... CUS2-ALL).

Each method is run, unchanged, on a VisitAllProblem: a wrapper whose states
are (location, destinations visited so far) and whose goal is any state
that has visited every destination. So each version keeps its own method's
behaviour - DFS's stack, BFS's goal test on generation and reached set, the
path cycle checks, the tie-breaking rules - only the question being asked
changes from "reach one destination" to "reach all of them".

Why the state must include the visited set: standing at node 3 having
visited {4} is a different situation from standing at node 3 having
visited {4, 5}. It also lets a route revisit a location, for example to back
out of a dead end that holds a destination. The cycle checks of DFS, GBFS,
AS, CUS1 and CUS2 (and BFS's reached set) now reject a repeat only when both
the location AND the visited set repeat, which is a genuine loop.

Heuristic (used by GBFS, AS and CUS2 through problem.heuristic): straight-
line distance to the NEAREST unvisited destination, plus the length of a
minimum spanning tree joining all the unvisited destinations. Any route that
visits them all must reach one of them and then pass through the rest, which
is at least as long as that tree, so as a length it never overestimates. AS
multiplies it by heuristic_scale and CUS2 divides it by the longest edge,
exactly as they do for a single goal, so both stay optimal for their measure
(cost for AS-ALL, moves for CUS1-ALL, CUS2-ALL and BFS-ALL).

The result is mapped back to ordinary nodes, so result.goal.path() is the
list of locations (which may repeat) and result.goal.state is the final
destination reached. nodes_created counts the nodes the method created in
the wrapped search, as usual.
"""

from collections import namedtuple

from ..node import Node, SearchResult
from ..problem import RouteProblem
from .visit_all import _mst_length

VisitState = namedtuple("VisitState", "location visited")
VisitState.__doc__ = "A location plus the frozenset of destinations visited on the way there."


class VisitAllProblem:
    """A RouteProblem whose goal is to have visited every destination.

    Offers the attributes and methods the search methods use: nodes,
    origin, destinations, successors, is_goal, distance and heuristic.
    nodes holds every (location, visited) state reachable from the origin,
    so methods that size themselves by len(problem.nodes) (CUS1's depth
    limit) or scan every edge (AS's heuristic scale, CUS2's longest edge)
    see the real wrapped graph.
    """

    def __init__(self, problem: RouteProblem):
        self.base = problem
        self.goals = frozenset(problem.destinations)
        self.origin = VisitState(problem.origin, self.goals & {problem.origin})
        self._tree_length = {}            # visited set -> MST length of the rest

        self._adjacency = {}
        pending = [self.origin]
        while pending:
            state = pending.pop()
            if state in self._adjacency:
                continue
            # base.successors is in ascending location order, and the visited
            # set is fixed by the location, so NOTE 2 ordering carries over.
            self._adjacency[state] = [
                (VisitState(location, state.visited | (self.goals & {location})), cost)
                for location, cost in problem.successors(state.location)]
            pending.extend(s for s, _ in self._adjacency[state] if s not in self._adjacency)

        self.nodes = {s: problem.nodes[s.location] for s in self._adjacency}
        self.destinations = frozenset(s for s in self.nodes if s.visited == self.goals)

    def successors(self, state):
        return self._adjacency[state]

    def is_goal(self, state):
        return state.visited == self.goals

    def distance(self, a, b):
        return self.base.distance(a.location, b.location)

    def heuristic(self, state):
        """Nearest unvisited destination + MST of the unvisited ones (0 when done)."""
        remaining = sorted(self.goals - state.visited)
        if not remaining:
            return 0.0
        if state.visited not in self._tree_length:
            self._tree_length[state.visited] = _mst_length(remaining, self.base.distance)
        nearest = min(self.base.distance(state.location, g) for g in remaining)
        return nearest + self._tree_length[state.visited]


def unwrap(goal):
    """Rebuild a wrapped goal Node's route as ordinary Nodes on locations."""
    if goal is None:
        return None
    node = None
    for wrapped in _chain(goal):
        node = Node(wrapped.state.location, node, wrapped.path_cost)
    return node


def _chain(node):
    chain = []
    while node is not None:
        chain.append(node)
        node = node.parent
    return reversed(chain)


def make_visit_all(method):
    """Return the visit-all version of a single-goal search method."""
    def search(problem):
        result = method(VisitAllProblem(problem))
        return SearchResult(unwrap(result.goal), result.nodes_created)

    search.__name__ = f"{method.__name__}_all"
    search.__doc__ = f"{method.__name__} on the visit-all problem (see module docstring)."
    search.base_method = method       # lets route_finding.trace find the real expand()
    return search
