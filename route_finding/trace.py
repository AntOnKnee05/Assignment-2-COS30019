"""Record the order in which a search method expands nodes.

Used by gui.py to replay a search step by step, and kept separate from the
GUI so it can be tested without tkinter.
"""

import sys


def trace_search(problem, method):
    """Run `method` on `problem` and record every node expansion in order.

    Returns (result, steps), where steps is a list of
    (expanded_state, [child states in the order they were generated]).

    Each algorithm module imports `expand` from route_finding.node, so the
    module's own reference is wrapped for the duration of the call. This
    records real expansions only: a neighbour check that does not create
    child nodes (such as the IDDFS cutoff test) is not logged as one. Child
    states are recorded as they are actually generated, so methods that stop
    part-way through a node's children show only the children they created.
    """
    module = sys.modules[method.__module__]
    original = module.expand
    steps = []

    def recording_expand(problem_, node):
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
