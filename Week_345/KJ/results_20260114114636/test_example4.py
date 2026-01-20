import unittest

from example4 import choose_num

class TestChooseNum(unittest.TestCase):

    def test_choose_num(self):
        self.assertEqual(choose_num(1, 10), 10)
        self.assertEqual(choose_num(1, 9), 8)
        self.assertEqual(choose_num(5, 5), -1)
        self.assertEqual(choose_num(10, 10), 10)
        self.assertEqual(choose_num(3, 3), -1)
        self.assertEqual(choose_num(2, 3), 2)
        self.assertEqual(choose_num(3, 4), 4)
        self.assertEqual(choose_num(-5, -3), -1)

if __name__ == '__main__':
    unittest.main()
