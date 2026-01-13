import unittest
from example3 import intersect

class TestIntersect(unittest.TestCase):

    def test_intersect_true(self):
        self.assertTrue(intersect(1, 1, 4, 4, 1, 4, 4, 1))  # Lines should intersect
        self.assertTrue(intersect(0, 0, 2, 2, 0, 2, 2, 0))  # Lines should intersect

    def test_intersect_false(self):
        self.assertFalse(intersect(1, 1, 2, 2, 3, 3, 4, 4))  # Lines should not intersect
        self.assertFalse(intersect(0, 0, 1, 1, 2, 2, 3, 3))  # Lines should not intersect

    def test_intersect_endpoint(self):
        self.assertTrue(intersect(0, 0, 2, 2, 1, 1, 3, 3))  # At endpoint
        self.assertTrue(intersect(1, 1, 1, 3, 1, 0, 1, 2))  # At vertical endpoint

if __name__ == '__main__':
    unittest.main()