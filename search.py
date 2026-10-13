"""Command-line entry point.

Usage:
    python search.py <filename> <method>

Output when a goal is reached:
    filename method
    goal number_of_nodes
    path
"""

import os
import sys

from route_finding import ParseError, parse_problem
from route_finding.algorithms import METHODS


def format_result(filename, method, result):
    """Build the output text required by the assignment spec."""
    lines = [f"{filename} {method}"]
    if result.goal is None:
        lines.append(f"No goal is reachable; {result.nodes_created}")
    else:
        lines.append(f"{result.goal.state} {result.nodes_created}")
        lines.append(" ".join(str(state) for state in result.goal.path()))
    return "\n".join(lines)


def main(argv):
    if len(argv) != 3:
        print(f"Usage: python {os.path.basename(argv[0])} <filename> <method>", file=sys.stderr)
        print(f"Methods: {', '.join(METHODS)}", file=sys.stderr)
        return 2

    filename, method = argv[1], argv[2].upper()
    if method not in METHODS:
        print(f"Unknown method '{argv[2]}'. Choose one of: {', '.join(METHODS)}", file=sys.stderr)
        return 2

    try:
        problem = parse_problem(filename)
    except OSError as e:
        print(f"Cannot read '{filename}': {e.strerror}", file=sys.stderr)
        return 1
    except ParseError as e:
        print(f"Invalid problem file '{filename}': {e}", file=sys.stderr)
        return 1

    try:
        result = METHODS[method](problem)
    except NotImplementedError as e:
        print(e, file=sys.stderr)
        return 1
    print(format_result(filename, method, result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
