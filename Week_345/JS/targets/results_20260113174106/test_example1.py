import pytest

def test_foo():
    assert foo(42, 0) == 1
    assert foo(42, 1) == 0
    assert foo(1, 0) == -1

def test_bar():
    assert bar(1, 2, 3) == 3
    assert bar(3, 2, 1) == 3
    assert bar(1, 2, 0) == 2
