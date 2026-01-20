import unittest
from example6 import prod_signs

class TestProdSigns(unittest.TestCase):

    def test_empty_array(self):
        self.assertIsNone(prod_signs([]))

    def test_all_positive(self):
        self.assertEqual(prod_signs([1, 2, 3]), 6)

    def test_all_negative(self):
        self.assertEqual(prod_signs([-1, -2, -3]), 6)

    def test_mixed(self):
        self.assertEqual(prod_signs([-1, 2, -3]), -6)
        self.assertEqual(prod_signs([-1, -2, 3]), 6)

    def test_with_zero(self):
        self.assertEqual(prod_signs([0, 1, -1]), 1)
        self.assertEqual(prod_signs([0, -2, 2]), 0)

if __name__ == '__main__':
    unittest.main()