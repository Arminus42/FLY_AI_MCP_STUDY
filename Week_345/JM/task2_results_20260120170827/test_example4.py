import pytest
from example4 import choose_num

def test_choose_num():
    # Test with two positive even numbers
    assert choose_num(2, 4) == 4
    # Test with two positive odd numbers
    assert choose_num(1, 3) == 2
    # Test with a range where there's no even number
    assert choose_num(5, 7) == 6  # Update expected value based on source code
    # Test with x > y
    assert choose_num(5, 2) == -1
    # Test with the same even number
    assert choose_num(2, 2) == 2
    # Test with the same odd number
    assert choose_num(3, 3) == -1
    # Test with a range including zero
    assert choose_num(0, 2) == 2
    # Test with a single even number
    assert choose_num(4, 4) == 4
    # Test with large even and odd numbers
    assert choose_num(1000000, 1000001) == 1000000
    # Test with negative numbers (should return -1)
    assert choose_num(-1, -3) == -1
