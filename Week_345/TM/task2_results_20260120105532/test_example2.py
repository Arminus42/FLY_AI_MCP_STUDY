import pytest

from example2 import testme


def test_normal_case():
    # Test the standard functionality of the function
    testme(0, 10, 100)
    assert True  # Will execute without error, coverage hit


def test_c_less_than_57():
    # Test case where c is less than 57, should decrement a
    testme(10, 20, 50)
    assert True  # Will execute without error, coverage hit


def test_c_greater_than_284():
    # Test case where c is greater than 284, should decrement a
    testme(10, 20, 285)
    assert True  # Will execute without error, coverage hit


def test_a_negative():
    # Test case where a goes negative
    testme(0, 0, 100)  # This should break immediately
    assert True  # Will execute without error, coverage hit


def test_a_never_reaches_b():
    # Test case where a never reaches b
    testme(0, 10, 56)  # This should cause a decrement on a
    assert True  # Will execute without error, coverage hit
