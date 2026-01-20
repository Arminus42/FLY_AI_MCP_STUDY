import example1
import pytest

def test_foo():
    assert example1.foo(42, 0) == 1
    assert example1.foo(42, 1) == 0
    assert example1.foo(0, 0) == -1
    assert example1.foo(42, -1) == 1
    assert example1.foo(41, 0) == -1

def test_bar():
    assert example1.bar(4, 6, 5) == 5
    assert example1.bar(6, 4, 5) == 6
    assert example1.bar(4, 6, 6) == 6
    assert example1.bar(6, 4, 4) == 6
    assert example1.bar(3, 3, 6) == 3