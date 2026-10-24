"""Command-line entry point.

Usage:
    python search.py <filename> <method>

Methods: DFS, BFS, GBFS, AS, CUS1, CUS2, and the research extension:
ALL (cheapest route that visits every destination) and DFS-ALL, BFS-ALL,
GBFS-ALL, AS-ALL, CUS1-ALL, CUS2-ALL (each required method searching for a
route that visits every destination). For these the goal printed is the
last destination reached and the path may repeat locations.

Output when a goal is reached:
    filename method
    goal number_of_nodes
    path
"""

import os
import sys

from route_finding import ParseError, parse_problem
from route_finding.algorithms import METHODS, RESEARCH_METHODS

ALL_METHODS = {**METHODS, **RESEARCH_METHODS}


def format_result(filename, method, result):
    """Build the output text required by the assignment spec."""
    lines = [f"{filename} {method}"]
    if result.goal is None:
        if method in RESEARCH_METHODS:
            lines.append(f"Not every destination is reachable; {result.nodes_created}")
        else:
            lines.append(f"No goal is reachable; {result.nodes_created}")
    else:
        lines.append(f"{result.goal.state} {result.nodes_created}")
        lines.append(" ".join(str(state) for state in result.goal.path()))
    return "\n".join(lines)


def main(argv):
    """Run one search from the command line; return the process exit code."""
    if len(argv) != 3:
        print(f"Usage: python {os.path.basename(argv[0])} <filename> <method>", file=sys.stderr)
        print(f"Methods: {', '.join(ALL_METHODS)}", file=sys.stderr)
        return 2

    filename, method = argv[1], argv[2].upper()
    if method not in ALL_METHODS:
        print(f"Unknown method '{argv[2]}'. Choose one of: {', '.join(ALL_METHODS)}", file=sys.stderr)
        return 2

    try:
        problem = parse_problem(filename)
    except OSError as e:
        print(f"Cannot read '{filename}': {e.strerror}", file=sys.stderr)
        return 1
    except ParseError as e:
        print(f"Invalid problem file '{filename}': {e}", file=sys.stderr)
        return 1

    result = ALL_METHODS[method](problem)
    print(format_result(filename, method, result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
