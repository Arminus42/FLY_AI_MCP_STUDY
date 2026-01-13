import pytest

def test_testme_positive_increment():
    a, b, c = 0, 10, 60
    testme(a, b, c)
    assert a == 1

def test_testme_negative_decrement():
    a, b, c = 10, 5, 60
    testme(a, b, c)
    assert a == 9


def test_testme_break_condition():
    a, b, c = 0, 10, 300
    testme(a, b, c)
    assert a < 0

def test_testme_no_change():
    a, b, c = 5, 5, 60
    testme(a, b, c)
    assert a == 5
