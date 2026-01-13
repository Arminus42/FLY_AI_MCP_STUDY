
import pytest

from example6.example6 import prod_signs


def test_prod_signs_empty():
    assert prod_signs([]) is None

def test_prod_signs_positive():
    assert prod_signs([1, 2, 3]) == 6

def test_prod_signs_negative():
    assert prod_signs([-1, -2, -3]) == -6

def test_prod_signs_mixed():
    assert prod_signs([1, 2, -3]) == -6

def test_prod_signs_with_zero():
    assert prod_signs([1, 2, 0, -3]) == 0

def test_prod_signs_single_positive():
    assert prod_signs([5]) == 5

def test_prod_signs_single_negative():
    assert prod_signs([-5]) == -5

def test_prod_signs_single_zero():
    assert prod_signs([0]) == 0

def test_prod_signs_large_numbers():
    assert prod_signs([1000000, 2000000, 3000000]) == 6000000000000000

def test_prod_signs_large_negative_numbers():
    assert prod_signs([-1000000, -2000000, -3000000]) == -6000000000000000

def test_prod_signs_mixed_large_numbers():
    assert prod_signs([1000000, -2000000, 3000000]) == -6000000000000000

def test_prod_signs_mixed_with_zero():
    assert prod_signs([1, -2, 0, 3, -4]) == 0

def test_prod_signs_all_zeros():
    assert prod_signs([0, 0, 0]) == 0

