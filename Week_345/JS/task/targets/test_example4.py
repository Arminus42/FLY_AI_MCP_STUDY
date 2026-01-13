
import pytest


def choose_num(x, y):
    """This function takes two positive numbers x and y and returns the
    biggest even integer number that is in the range [x, y] inclusive. If 
    there's no such number, then the function should return -1.
    """
    if x > y:
        return -1
    if y % 2 == 0:
        return y
    if x == y:
        return -1
    return y - 1


def test_choose_num_even_y():
    assert choose_num(2, 10) == 10

def test_choose_num_odd_y_even_x():
    assert choose_num(2, 9) == 8

def test_choose_num_even_y_odd_x():
    assert choose_num(3, 10) == 10

def test_choose_num_odd_y_odd_x():
    assert choose_num(3, 9) == 8

def test_choose_num_no_even_in_range():
    assert choose_num(3, 3) == -1

def test_choose_num_no_even_in_range_single_odd():
    assert choose_num(5, 5) == -1

def test_choose_num_no_even_in_range_single_even():
    assert choose_num(4, 4) == 4

def test_choose_num_x_greater_than_y():
    assert choose_num(10, 2) == -1

def test_choose_num_large_numbers():
    assert choose_num(100, 200) == 200

def test_choose_num_large_numbers_odd_y():
    assert choose_num(100, 199) == 198
