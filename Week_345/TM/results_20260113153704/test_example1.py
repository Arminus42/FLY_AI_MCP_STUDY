import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/example1')))

import example1


def test_foo():
    assert example1.foo(42, 0) == 1
    assert example1.foo(42, 5) == 0
    assert example1.foo(10, 5) == -1


def test_bar():
    assert example1.bar(4, 6, 5) == 5
    assert example1.bar(10, 8, 6) == 10
    assert example1.bar(2, 3, 5) == 5
