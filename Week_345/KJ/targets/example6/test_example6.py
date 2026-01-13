import unittest
from example6 import prod_signs

class TestProdSigns(unittest.TestCase):

    def test_positive_numbers(self):
        self.assertEqual(prod_signs([1, 2, 3]), 6)

    def test_negative_numbers(self):
        self.assertEqual(prod_signs([-1, -2, -3]), -6)

    def test_mixed_numbers(self):
        self.assertEqual(prod_signs([-1, 0, 2]), 2)

    def test_zero_in_array(self):
        self.assertEqual(prod_signs([0, 1, -1]), 0)

    def test_empty_array(self):
        self.assertIsNone(prod_signs([]))

    def test_single_positive_number(self):
        self.assertEqual(prod_signs([5]), 5)

    def test_single_negative_number(self):
        self.assertEqual(prod_signs([-5]), -5)

    def test_single_zero(self):
        self.assertEqual(prod_signs([0]), 0)

if __name__ == '__main__':
    unittest.main()