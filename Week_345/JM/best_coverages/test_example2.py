import pytest

from example2 import testme

def test_case_1():
    assert testme(10, 20, 100) is None  # Normal case


def test_case_2():
    assert testme(5, 5, 100) is None  # Edge case where a == b


def test_case_3():
    assert testme(-1, 20, 100) is None  # Edge case where a is negative


def test_case_4():
    assert testme(10, 20, 300) is None  # Edge case where c is greater than 284


def test_case_5():
    assert testme(10, 20, 0) is None  # Edge case where c is less than 57
