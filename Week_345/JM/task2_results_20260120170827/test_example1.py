import pytest

from example1 import foo, bar

class TestExample1:

    def test_foo_with_42_and_0(self):
        assert foo(42, 0) == 1  # Line covered

    def test_foo_with_42_and_non_zero(self):
        assert foo(42, 1) == 0  # Line covered

    def test_foo_with_non_42(self):
        assert foo(10, 10) == -1  # Line covered

    def test_bar_greater_than_z(self):
        assert bar(10, 20, 10) == 10  # Updated line, fixed assertion

    def test_bar_less_than_z_and_greater_x(self):
        assert bar(10, 5, 8) == 10  # Line covered

    def test_bar_else_case(self):
        assert bar(2, 3, 5) == 3  # Line covered
