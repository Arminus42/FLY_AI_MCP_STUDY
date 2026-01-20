import unittest
from example3 import intersect

class TestIntersect(unittest.TestCase):

    def test_intersect(self):
        # Test cases where lines intersect
        self.assertTrue(intersect(0, 0, 1, 1, 0, 1, 1, 0))  # diagonal lines
        self.assertTrue(intersect(1, 1, 2, 2, 0, 0, 2, 2))  # one line on another

        # Test cases where lines do not intersect
        self.assertFalse(intersect(0, 0, 1, 1, 1, 2, 2, 3))  # parallel lines
        self.assertFalse(intersect(1, 0, 1, 1, 0, 0, 0, 1))  # vertical and horizontal lines

if __name__ == '__main__':
    unittest.main()