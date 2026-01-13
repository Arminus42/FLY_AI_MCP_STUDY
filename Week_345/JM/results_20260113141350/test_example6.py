import unittest
from example6.example6 import prod_signs

class TestProdSigns(unittest.TestCase):
    def test_empty_array(self):
        self.assertIsNone(prod_signs([]))

    def test_single_positive(self):
        self.assertEqual(prod_signs([5]), 5)

    def test_single_negative(self):
        self.assertEqual(prod_signs([-5]), -5)

    def test_mixed_numbers(self):
        self.assertEqual(prod_signs([-1, 2, -3]), -4)
        self.assertEqual(prod_signs([-1, -2, -3]), -6)
        self.assertEqual(prod_signs([1, 2, 3]), 6)

    def test_contains_zero(self):
        self.assertEqual(prod_signs([-1, 0, 1]), 0)
        self.assertEqual(prod_signs([0]), 0)

if __name__ == '__main__':
    unittest.main()