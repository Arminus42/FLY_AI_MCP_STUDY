import pytest
from example1 import foo, bar


def test_foo_x_equals_42_y_equals_0():
    assert foo(42, 0) == 1  # Test case where x is 42 and y is 0


def test_foo_x_equals_42_y_not_0():
    assert foo(42, 1) == 0  # Test case where x is 42 and y is non-zero


def test_foo_x_not_42():
    assert foo(10, 5) == -1  # Test case where x is not 42


def test_bar_avg_greater_than_z():
    assert bar(5, 10, 4) == 4   # Average is greater than z


def test_bar_avg_less_than_z_and_x_greater_than_y():
    assert bar(8, 2, 5) == 8   # Average less than z and x > y


def test_bar_else_case():
    assert bar(3, 7, 5) == 7   # Else case for bar function


def test_bar_avg_equals_z():
    assert bar(4, 4, 4) == 4   # Boundary case where average equals z
