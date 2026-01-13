import unittest

from example2 import testme

class TestExample2(unittest.TestCase):

    def test_case_1(self):
        self.assertIsNone(testme(10, 20, 60))  # Test with c in the range

    def test_case_2(self):
        self.assertIsNone(testme(10, 20, 50))  # Test with c out of the range

    def test_case_3(self):
        self.assertIsNone(testme(10, 10, 100))  # Test when a is equal to b

    def test_case_4(self):
        self.assertIsNone(testme(-1, 20, 100))  # Test starting with a below 0

if __name__ == '__main__':
    unittest.main()