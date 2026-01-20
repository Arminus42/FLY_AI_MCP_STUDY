import pytest
from example4 import choose_num


def test_choose_num_with_large_range():
    assert choose_num(1, 10) == 10  # 10 is the largest even number


def test_choose_num_with_no_even_numbers():
    assert choose_num(3, 5) == -1  # No even numbers in range 3 to 5


def test_choose_num_with_single_even_number():
    assert choose_num(4, 4) == 4  # Only one number which is even


def test_choose_num_with_x_greater_than_y():
    assert choose_num(5, 3) == -1  # x greater than y


def test_choose_num_with_both_numbers_even():
    assert choose_num(6, 8) == 8  # 8 is the largest even number


def test_choose_num_with_both_numbers_odd():
    assert choose_num(5, 7) == -1  # No even numbers available


def test_choose_num_with_large_odd_range():
    assert choose_num(11, 15) == -1  # No even numbers available


def test_choose_num_with_large_even_range():
    assert choose_num(10, 20) == 20  # 20 is the largest even number


def test_choose_num_with_x_equals_y_odd():
    assert choose_num(7, 7) == -1  # x equals y, and it is odd
