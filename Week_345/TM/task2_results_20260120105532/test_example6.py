import pytest
from example6 import prod_signs

def test_prod_signs_empty():
    assert prod_signs([]) is None

def test_prod_signs_all_positive():
    assert prod_signs([1, 2, 3]) == 6


def test_prod_signs_one_negative():
    assert prod_signs([-1]) == -1


def test_prod_signs_multiple_negatives():
    assert prod_signs([-1, -2]) == -3


def test_prod_signs_mixed():
    assert prod_signs([-1, 2, -3]) == 4


def test_prod_signs_with_zero():
    assert prod_signs([1, 0, -3]) == 0
