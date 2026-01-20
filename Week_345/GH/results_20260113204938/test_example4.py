import unittest

# Assuming the function is defined in a file named example4.py
# from example4 import choose_num

def choose_num(x, y):
    """This function takes two positive numbers x and y and returns the
    biggest even integer number that is in the range [x, y] inclusive. If 
    there's no such number, then the function should return -1.
    """
    if x > y:
        return -1
    if y % 2 == 0:
        return y
    if x == y:
        return -1
    return y - 1

class TestChooseNum(unittest.TestCase):

    def test_case_1(self):
        self.assertEqual(choose_num(1, 10), 10)

    def test_case_2(self):
        self.assertEqual(choose_num(1, 9), 8)

    def test_case_3(self):
        self.assertEqual(choose_num(3, 3), -1)

    def test_case_4(self):
        self.assertEqual(choose_num(10, 10), 10)

    def test_case_5(self):
        self.assertEqual(choose_num(5, 15), 14)

    def test_case_6(self):
        self.assertEqual(choose_num(20, 10), -1)  # x > y

if __name__ == '__main__':
    unittest.main()