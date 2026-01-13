import unittest
from example4 import choose_num

class TestChooseNum(unittest.TestCase):

    def test_choose_num(self):
        # Test with positive numbers where y is even
        self.assertEqual(choose_num(1, 10), 10)
        self.assertEqual(choose_num(5, 20), 20)

        # Test with positive numbers where y is odd
        self.assertEqual(choose_num(1, 9), 8)
        self.assertEqual(choose_num(5, 15), 14)

        # Test with a range that has no even integers
        self.assertEqual(choose_num(5, 5), -1)
        self.assertEqual(choose_num(3, 5), -1)

        # Test with x greater than y
        self.assertEqual(choose_num(10, 5), -1)

        # Test with no integers in the range
        self.assertEqual(choose_num(8, 9), 8)

if __name__ == '__main__':
    unittest.main()