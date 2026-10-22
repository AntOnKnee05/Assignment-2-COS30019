"""Unit tests for the problem parser."""

import os
import tempfile
import unittest

from helpers import CASES_DIR
from route_finding import ParseError, parse_problem, parse_problem_text

VALID = "Nodes:\n1: (0,0)\n2: (3,4)\nEdges:\n(1,2): 5\nOrigin:\n1\nDestinations:\n2\n"


class ParserTests(unittest.TestCase):
    def test_spec_example(self):
        problem = parse_problem(CASES_DIR / "test01_spec_example.txt")
        self.assertEqual(len(problem.nodes), 6)
        self.assertEqual(problem.nodes[1], (4, 1))
        self.assertEqual(problem.origin, 2)
        self.assertEqual(problem.destinations, {4, 5})
        # Successors come out in ascending node order.
        self.assertEqual(problem.successors(3), [(1, 5), (2, 5), (5, 6), (6, 7)])
        # Edges are directed: 2 -> 1 exists, 1 -> 2 does not.
        self.assertIn((1, 4), problem.successors(2))
        self.assertNotIn(2, [n for n, _ in problem.successors(1)])

    def test_inline_values_and_whitespace(self):
        problem = parse_problem_text(
            "Nodes:\n 1 : ( 0 , 0 )\n2: (3,4)\n\nEdges:\n(1, 2): 5\nOrigin: 1\nDestinations: 2\n")
        self.assertEqual(problem.origin, 1)
        self.assertEqual(problem.destinations, {2})
        self.assertAlmostEqual(problem.heuristic(1), 5.0)

    def test_decimals_negatives_and_multiple_destinations(self):
        problem = parse_problem_text(
            "Nodes:\n1: (-1.5,0)\n2: (2,2.25)\n3: (0,0)\nEdges:\n(1,2): 0.5\n"
            "Origin:\n1\nDestinations:\n2 ; 3;\n")
        self.assertEqual(problem.nodes[1], (-1.5, 0))
        self.assertEqual(problem.successors(1), [(2, 0.5)])
        self.assertEqual(problem.destinations, {2, 3})

    def test_headers_are_case_insensitive(self):
        problem = parse_problem_text(VALID.replace("Nodes:", "NODES:").replace("Origin:", "origin:"))
        self.assertEqual(problem.origin, 1)

    def test_windows_line_endings_and_byte_order_mark(self):
        # Notepad can save UTF-8 with a BOM and CRLF line endings.
        with tempfile.NamedTemporaryFile("wb", suffix=".txt", delete=False) as f:
            f.write(b"\xef\xbb\xbf" + VALID.replace("\n", "\r\n").encode())
        try:
            self.assertEqual(parse_problem(f.name).destinations, {2})
        finally:
            os.remove(f.name)

    def test_errors_are_reported_as_parse_errors(self):
        bad_files = {
            "undeclared node": VALID.replace("(1,2): 5", "(1,9): 5"),
            "missing origin": VALID.replace("Origin:\n1\n", ""),
            "missing destinations": VALID.replace("Destinations:\n2\n", ""),
            "non-numeric origin": VALID.replace("Origin:\n1", "Origin:\nA"),
            "two origins on one line": VALID.replace("Origin:\n1", "Origin:\n1 2"),
            "two origin lines": VALID.replace("Origin:\n1", "Origin:\n1\n2"),
            "comma-separated destinations": VALID.replace("Destinations:\n2", "Destinations:\n1, 2"),
            "duplicate node": VALID.replace("2: (3,4)", "2: (3,4)\n2: (5,5)"),
            "negative cost": VALID.replace("(1,2): 5", "(1,2): -5"),
            "malformed node": VALID.replace("2: (3,4)", "2: 3,4"),
            "content before any section": "hello\n" + VALID,
        }
        for name, text in bad_files.items():
            with self.subTest(name), self.assertRaises(ParseError):
                parse_problem_text(text)


if __name__ == "__main__":
    unittest.main()
