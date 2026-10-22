"""Lock the exact output of all 90 method/case runs.

tests/cases/expected_results.json holds the goal, number_of_nodes and path
that each method produced when the report figures were measured. If a code
change alters any of them, this test fails so the report can be checked.
After an intentional change, regenerate the file with:

    python tests/update_expected_results.py
"""

import json
import unittest

from helpers import CASES_DIR, fixture_paths
from route_finding import parse_problem
from route_finding.algorithms import METHODS


class RegressionTests(unittest.TestCase):
    def test_every_method_on_every_case_matches_recorded_output(self):
        expected = json.loads((CASES_DIR / "expected_results.json").read_text())
        self.assertEqual(sorted(expected), [p.name for p in fixture_paths()],
                         "fixtures changed: regenerate expected_results.json")
        for case in fixture_paths():
            problem = parse_problem(case)
            for method, run in METHODS.items():
                with self.subTest(case=case.name, method=method):
                    result = run(problem)
                    goal = result.goal
                    self.assertEqual({
                        "goal": goal.state if goal else None,
                        "nodes_created": result.nodes_created,
                        "path": goal.path() if goal else None,
                    }, expected[case.name][method])


if __name__ == "__main__":
    unittest.main()
