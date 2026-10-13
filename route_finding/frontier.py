"""Priority-queue frontier with the assignment's tie-breaking rules.

NOTE 2 of the spec: when priorities are equal, expand the smaller node id
first; between nodes on different branches, expand the one added earlier
first. Children are generated in ascending order (see node.expand), so a
global insertion counter gives both behaviours.

If the team decides to break ties on node id before insertion order,
change the key in `push` to (priority, node.state, counter) - confirm the
interpretation with the tutor and document it in the report.
"""

import heapq
import itertools


class PriorityFrontier:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def push(self, node, priority):
        heapq.heappush(self._heap, (priority, next(self._counter), node))

    def pop(self):
        return heapq.heappop(self._heap)[-1]

    def __len__(self):
        return len(self._heap)

    def __bool__(self):
        return bool(self._heap)
