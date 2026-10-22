"""PriorityFrontier ordering, including the NOTE 2 tie-breaking rule."""

import unittest

from route_finding.frontier import PriorityFrontier


class FrontierTests(unittest.TestCase):
    def test_lowest_priority_first(self):
        frontier = PriorityFrontier()
        for item, priority in [("c", 3), ("a", 1), ("b", 2)]:
            frontier.push(item, priority)
        self.assertEqual([frontier.pop() for _ in range(3)], ["a", "b", "c"])
        self.assertFalse(frontier)

    def test_ties_pop_in_insertion_order(self):
        frontier = PriorityFrontier()
        for item in ["first", "second", "third"]:
            frontier.push(item, 5)
        self.assertEqual([frontier.pop() for _ in range(3)], ["first", "second", "third"])

    def test_floating_point_noise_still_counts_as_a_tie(self):
        frontier = PriorityFrontier()
        frontier.push("first", 0.1 + 0.2)   # 0.30000000000000004
        frontier.push("second", 0.3)
        self.assertEqual(frontier.pop(), "first")

    def test_len(self):
        frontier = PriorityFrontier()
        frontier.push("x", 1)
        self.assertEqual(len(frontier), 1)


if __name__ == "__main__":
    unittest.main()
