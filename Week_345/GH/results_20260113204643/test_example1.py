import unittest

# Assuming example1.py has been imported correctly
# from example1 import foo, bar

def foo(x: int, y: int) -> int:
    z = 0
    if x == 42:
        if y == 0:
            z = 1
        else:
            z = 0
    else:
        z = -1
    return z


def bar(x: int, y: int, z: int) -> int:
    if (x + y) / 2 > z:
        return z
    elif (x + y) / 3 < z and x > y:
        return x
    else:
        return y

class TestExample1(unittest.TestCase):

    def test_foo(self):
        self.assertEqual(foo(42, 0), 1)
        self.assertEqual(foo(42, 1), 0)
        self.assertEqual(foo(41, 0), -1)

    def test_bar(self):
        self.assertEqual(bar(10, 5, 6), 6)
        self.assertEqual(bar(10, 5, 4), 10)
        self.assertEqual(bar(10, 5, 5), 5)


if __name__ == '__main__':
    unittest.main()