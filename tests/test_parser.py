"""Unit tests for the problem parser. Run with: python -m unittest discover tests"""

import os
import unittest

from route_finding import ParseError, parse_problem, parse_problem_text

CASES = os.path.join(os.path.dirname(__file__), "cases")


class ParserTests(unittest.TestCase):
    def test_spec_example(self):
        problem = parse_problem(os.path.join(CASES, "test01_spec_example.txt"))
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
            "Nodes:\n 1 : ( 0 , 0 )\n2: (3,4)\n\nEdges:\n(1, 2): 5\nOrigin: 1\nDestinations: 2\n"
        )
        self.assertEqual(problem.origin, 1)
        self.assertEqual(problem.destinations, {2})
        self.assertAlmostEqual(problem.heuristic(1), 5.0)

    def test_undeclared_node_rejected(self):
        with self.assertRaises(ParseError):
            parse_problem_text("Nodes:\n1: (0,0)\nEdges:\n(1,9): 1\nOrigin:\n1\nDestinations:\n1\n")

    def test_missing_origin_rejected(self):
        with self.assertRaises(ParseError):
            parse_problem_text("Nodes:\n1: (0,0)\nEdges:\nDestinations:\n1\n")


if __name__ == "__main__":
    unittest.main()
