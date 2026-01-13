import unittest
from example3.example3 import intersect

class TestIntersect(unittest.TestCase):
    def test_lines_intersect(self):
        self.assertTrue(intersect(1, 1, 4, 4, 1, 4, 4, 1))  # Diagonal lines intersect
        self.assertTrue(intersect(1, 1, 4, 1, 2, 2, 2, 0))  # Vertical and horizontal intersect

    def test_lines_do_not_intersect(self):
        self.assertFalse(intersect(1, 1, 2, 2, 3, 3, 4, 4))  # Parallel lines
        self.assertFalse(intersect(0, 0, 1, 1, 1, 0, 2, 0))  # Lines do not intersect

    def test_edge_cases(self):
        self.assertTrue(intersect(0, 0, 1, 1, 0, 0, 1, 1))  # Coincident points
        self.assertTrue(intersect(0, 0, 1, 1, 0, 0, 1, 0))  # Vertical line case

if __name__ == '__main__':
    unittest.main()