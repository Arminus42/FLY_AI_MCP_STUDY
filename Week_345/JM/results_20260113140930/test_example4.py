import unittest
from example4.example4 import choose_num

class TestChooseNum(unittest.TestCase):

    def test_even_range(self):
        self.assertEqual(choose_num(1, 10), 10)
        self.assertEqual(choose_num(3, 9), 8)
        self.assertEqual(choose_num(4, 4), 4)

    def test_odd_range(self):
        self.assertEqual(choose_num(1, 9), 8)
        self.assertEqual(choose_num(5, 5), -1)

    def test_no_valid_even(self):
        self.assertEqual(choose_num(5, 7), -1)
        self.assertEqual(choose_num(9, 11), 10)

    def test_reverse_order(self):
        self.assertEqual(choose_num(10, 1), -1)

if __name__ == '__main__':
    unittest.main()