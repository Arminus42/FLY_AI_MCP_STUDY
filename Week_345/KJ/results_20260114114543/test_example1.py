import unittest

class TestExample1(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(foo(42, 0), 1)
        self.assertEqual(foo(42, 1), 0)
        self.assertEqual(foo(1, 1), -1)

    def test_bar(self):
        self.assertEqual(bar(2, 4, 3), 3)
        self.assertEqual(bar(6, 3, 4), 6)
        self.assertEqual(bar(1, 2, 1), 2)

if __name__ == '__main__':
    unittest.main()