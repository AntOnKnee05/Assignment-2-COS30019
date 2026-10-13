"""Run every method on every test case and print a summary table.

Usage:
    python run_tests.py                  # all cases in tests/cases
    python run_tests.py --csv results.csv  # also save results for the report

Useful for the Testing and Insights sections of the report.
"""

import argparse
import csv
import glob
import os
import time

from route_finding import parse_problem
from route_finding.algorithms import METHODS

CASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "cases")


def run_case(path, method):
    """Run one method on one file and return a result row (dict)."""
    row = {"case": os.path.basename(path), "method": method}
    try:
        problem = parse_problem(path)
        start = time.perf_counter()
        result = METHODS[method](problem)
        row["time_ms"] = round((time.perf_counter() - start) * 1000, 3)
    except NotImplementedError:
        return {**row, "status": "not implemented"}
    except Exception as e:  # report any crash instead of stopping the batch
        return {**row, "status": f"error: {type(e).__name__}: {e}"}

    row["nodes_created"] = result.nodes_created
    if result.goal is None:
        row["status"] = "no solution"
    else:
        row["status"] = "ok"
        row["goal"] = result.goal.state
        row["cost"] = result.goal.path_cost
        row["moves"] = result.goal.depth
        row["path"] = " ".join(map(str, result.goal.path()))
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cases", default=os.path.join(CASES_DIR, "*.txt"), help="glob of problem files")
    parser.add_argument("--methods", nargs="+", default=list(METHODS), help="methods to run")
    parser.add_argument("--csv", help="write results to this CSV file")
    args = parser.parse_args()

    columns = ["case", "method", "status", "goal", "nodes_created", "cost", "moves", "time_ms", "path"]
    rows = [run_case(path, m.upper()) for path in sorted(glob.glob(args.cases)) for m in args.methods]

    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns} if rows else {}
    print("  ".join(c.ljust(widths[c]) for c in columns))
    for r in rows:
        print("  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nSaved {len(rows)} rows to {args.csv}")


if __name__ == "__main__":
    main()
