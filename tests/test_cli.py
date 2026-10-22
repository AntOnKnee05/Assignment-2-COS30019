"""End-to-end tests of search.py, the program the marker will run."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import CASES_DIR

PROJECT = Path(__file__).resolve().parent.parent
EXAMPLE = os.path.join("tests", "cases", "test01_spec_example.txt")


def run(*args):
    return subprocess.run([sys.executable, "search.py", *args], cwd=PROJECT,
                          capture_output=True, text=True)


class CommandLineTests(unittest.TestCase):
    def test_required_output_format_for_every_method(self):
        expected = json.loads((CASES_DIR / "expected_results.json").read_text())
        for method, row in expected["test01_spec_example.txt"].items():
            with self.subTest(method=method):
                proc = run(EXAMPLE, method)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(proc.stdout.splitlines(), [
                    f"{EXAMPLE} {method}",
                    f"{row['goal']} {row['nodes_created']}",
                    " ".join(map(str, row["path"])),
                ])

    def test_method_name_is_case_insensitive(self):
        self.assertEqual(run(EXAMPLE, "bfs").stdout.splitlines()[0], f"{EXAMPLE} BFS")

    def test_unreachable_goal(self):
        proc = run(os.path.join("tests", "cases", "test03_unreachable.txt"), "BFS")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("No goal is reachable", proc.stdout)

    def test_wrong_argument_count(self):
        proc = run(EXAMPLE)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Usage", proc.stderr)

    def test_unknown_method(self):
        proc = run(EXAMPLE, "XYZ")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Unknown method", proc.stderr)

    def test_missing_file(self):
        proc = run("no_such_file.txt", "BFS")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Cannot read", proc.stderr)

    def test_malformed_file_gives_message_not_traceback(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("Nodes:\n1: (0,0)\nOrigin:\nA\nDestinations:\n1\n")
        try:
            proc = run(f.name, "BFS")
        finally:
            os.remove(f.name)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Invalid problem file", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


if __name__ == "__main__":
    unittest.main()
