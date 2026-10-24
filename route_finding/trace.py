"""Record the order in which a search method expands nodes.

Used by gui.py to replay a search step by step, and kept separate from the
GUI so it can be tested without tkinter.
"""

import sys


class TraceLimitExceeded(Exception):
    """The search made more expansions than trace_search was allowed to record."""


def trace_search(problem, method, max_steps=None):
    """Run `method` on `problem` and record every node expansion in order.

    Returns (result, steps), where steps is a list of
    (expanded_state, [child states in the order they were generated]).

    Each algorithm module imports `expand` from route_finding.node, so the
    module's own reference is wrapped for the duration of the call. This
    records real expansions only: a neighbour check that does not create
    child nodes (such as the IDDFS cutoff test) is not logged as one. Child
    states are recorded as they are actually generated, so methods that stop
    part-way through a node's children show only the children they created.

    A visit-all wrapper (see visit_all_methods.make_visit_all) names the
    method it runs as base_method; that method's module is the one patched,
    and the states logged are VisitState(location, visited) pairs.

    If max_steps is given and the search tries to make more expansions than
    that, the search is abandoned and TraceLimitExceeded is raised, so the GUI
    is not frozen by a search too large to animate.
    """
    module = sys.modules[getattr(method, "base_method", method).__module__]
    original = module.expand
    steps = []

    def recording_expand(problem_, node):
        if max_steps is not None and len(steps) >= max_steps:
            raise TraceLimitExceeded(f"more than {max_steps} expansions")
        children = []
        steps.append((node.state, children))
        for child in original(problem_, node):
            children.append(child.state)
            yield child

    module.expand = recording_expand
    try:
        result = method(problem)
    finally:
        module.expand = original
    return result, steps
