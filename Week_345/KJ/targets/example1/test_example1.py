import unittest
from example1 import foo, bar

class TestExample1(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(foo(42, 0), 1)  # Test case where x is 42 and y is 0
        self.assertEqual(foo(42, 1), 0)  # Test case where x is 42 and y is not 0
        self.assertEqual(foo(41, 0), -1)  # Test case where x is not 42

    def test_bar(self):
        self.assertEqual(bar(6, 6, 5), 5)  # Test case where average of x and y is greater than z
        self.assertEqual(bar(6, 4, 5), 6)  # Test case where average of x and y is less than z
        self.assertEqual(bar(4, 6, 5), 6)  # Test case where average of x and y is less than z and x is less than y

if __name__ == '__main__':
    unittest.main()