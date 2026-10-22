"""Regenerate tests/cases/expected_results.json after an intentional change.

Run from the project folder:  python tests/update_expected_results.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from route_finding import parse_problem  # noqa: E402
from route_finding.algorithms import METHODS  # noqa: E402

CASES_DIR = Path(__file__).resolve().parent / "cases"

results = {}
for case in sorted(CASES_DIR.glob("test*.txt")):
    problem = parse_problem(case)
    results[case.name] = {}
    for method, run in METHODS.items():
        result = run(problem)
        goal = result.goal
        results[case.name][method] = {
            "goal": goal.state if goal else None,
            "nodes_created": result.nodes_created,
            "path": goal.path() if goal else None,
        }

(CASES_DIR / "expected_results.json").write_text(json.dumps(results, indent=2) + "\n")
print(f"Recorded {len(results) * len(METHODS)} results")
