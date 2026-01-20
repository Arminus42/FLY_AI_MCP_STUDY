import unittest
from example3 import intersect

class TestIntersect(unittest.TestCase):
    
    def test_intersect_true(self):
        self.assertTrue(intersect(1, 1, 4, 4, 1, 4, 4, 1))  # Lines should intersect
        self.assertTrue(intersect(0, 0, 2, 2, 0, 2, 2, 0))  # Lines should intersect
        self.assertTrue(intersect(0, 0, 1, 1, 0, 1, 1, 0))  # Lines should intersect

    def test_intersect_false(self):
        self.assertFalse(intersect(1, 1, 2, 2, 3, 3, 4, 4))  # Lines should not intersect
        self.assertFalse(intersect(0, 0, 1, 0, 0, 1, 1, 1))  # Lines should not intersect

    def test_intersect_edge_cases(self):
        self.assertTrue(intersect(1, 1, 2, 2, 1, 1, 2, 2))  # Edge case, same line
        self.assertFalse(intersect(1, 1, 2, 2, 1, 2, 2, 1))  # Edge case, touching but not intersecting

if __name__ == '__main__':
    unittest.main()