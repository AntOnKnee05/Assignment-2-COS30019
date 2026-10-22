"""Parser for Route Finding problem files.

File format (see assignment spec):

    Nodes:
    1: (4,1)
    ...
    Edges:
    (2,1): 4
    ...
    Origin:
    2
    Destinations:
    5; 4
"""

import re

from .problem import RouteProblem

_NODE_RE = re.compile(r"^\s*(\d+)\s*:\s*\(\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)\s*$")
_EDGE_RE = re.compile(r"^\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*:\s*(\d+(?:\.\d+)?)\s*$")
_SECTIONS = ("nodes", "edges", "origin", "destinations")


class ParseError(ValueError):
    """Raised when a problem file does not match the expected format."""


def _to_number(text):
    """Return an int when the value is whole, otherwise a float."""
    value = float(text)
    return int(value) if value.is_integer() else value


def _to_node_id(text, line_no, what):
    """Convert a node id in the Origin/Destinations sections, or raise ParseError."""
    text = text.strip()
    if not text.isdigit():
        raise ParseError(f"line {line_no}: {what} must be a node number, got '{text}'")
    return int(text)


def parse_problem(path):
    """Read the problem file at `path` and return a RouteProblem."""
    # utf-8-sig also accepts files saved by Windows Notepad with a byte-order mark.
    with open(path, encoding="utf-8-sig") as f:
        return parse_problem_text(f.read())


def parse_problem_text(text):
    """Parse the contents of a problem file and return a RouteProblem."""
    nodes = {}
    edges = []
    origin = None
    destinations = []
    section = None

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue

        # A section header may have content on the same line, e.g. "Origin: 2".
        header, sep, rest = line.partition(":")
        if sep and header.strip().lower() in _SECTIONS:
            section = header.strip().lower()
            line = rest.strip()
            if not line:
                continue

        if section == "nodes":
            match = _NODE_RE.match(line)
            if not match:
                raise ParseError(f"line {line_no}: bad node '{raw}'")
            node_id, x, y = int(match.group(1)), match.group(2), match.group(3)
            if node_id in nodes:
                raise ParseError(f"line {line_no}: node {node_id} is declared twice")
            nodes[node_id] = (_to_number(x), _to_number(y))
        elif section == "edges":
            match = _EDGE_RE.match(line)
            if not match:
                raise ParseError(f"line {line_no}: bad edge '{raw}'")
            src, dst, cost = match.groups()
            edges.append((int(src), int(dst), _to_number(cost)))
        elif section == "origin":
            if origin is not None:
                raise ParseError(f"line {line_no}: more than one origin")
            origin = _to_node_id(line, line_no, "Origin")
        elif section == "destinations":
            destinations.extend(_to_node_id(d, line_no, "each destination")
                                for d in line.split(";") if d.strip())
        else:
            raise ParseError(f"line {line_no}: content outside any section '{raw}'")

    if origin is None:
        raise ParseError("missing Origin")
    if not destinations:
        raise ParseError("missing Destinations")
    for node_id in [origin, *destinations] + [n for e in edges for n in e[:2]]:
        if node_id not in nodes:
            raise ParseError(f"node {node_id} is used but not declared under Nodes")

    return RouteProblem(nodes, edges, origin, destinations)
