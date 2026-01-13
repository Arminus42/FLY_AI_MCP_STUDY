import unittest

from example1 import foo, bar

class TestExample1(unittest.TestCase):
    def test_foo(self):
        self.assertEqual(foo(42, 0), 1)
        self.assertEqual(foo(42, 1), 0)
        self.assertEqual(foo(41, 0), -1)

    def test_bar(self):
        self.assertEqual(bar(2, 4, 3), 3)
        self.assertEqual(bar(4, 2, 3), 4)
        self.assertEqual(bar(2, 3, 2), 2)

if __name__ == '__main__':
    unittest.main()