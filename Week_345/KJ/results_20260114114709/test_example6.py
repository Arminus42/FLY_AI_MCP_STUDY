import unittest

from example6 import prod_signs

class TestProdSigns(unittest.TestCase):

    def test_empty_array(self):
        self.assertIsNone(prod_signs([]))

    def test_positive_numbers(self):
        self.assertEqual(prod_signs([1, 2, 3]), 6)

    def test_negative_numbers(self):
        self.assertEqual(prod_signs([-1, -2, -3]), -6)

    def test_mixed_numbers(self):
        self.assertEqual(prod_signs([-1, 2, -3]), 6)

    def test_zero_in_array(self):
        self.assertEqual(prod_signs([-1, 0, 2, 3]), 0)

    def test_all_zeroes(self):
        self.assertEqual(prod_signs([0, 0, 0]), 0)

if __name__ == '__main__':
    unittest.main()