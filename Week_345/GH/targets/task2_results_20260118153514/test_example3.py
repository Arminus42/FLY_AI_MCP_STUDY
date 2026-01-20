import example3
import pytest

def test_intersect_true():
    assert example3.intersect(0, 0, 1, 1, 0, 1, 1, 0) == True
    assert example3.intersect(0, 0, 2, 2, 1, 1, 3, 3) == True
    assert example3.intersect(1, 1, 1, 0, 0, 1, 1, -1) == True

def test_intersect_false():
    assert example3.intersect(0, 0, 1, 1, 2, 2, 3, 3) == False
    assert example3.intersect(0, 0, 0, 1, 1, 1, 1, 0) == False
    assert example3.intersect(0, 0, 1, 1, 2, 0, 3, 0) == False

def test_intersect_collinear():
    assert example3.intersect(0, 0, 2, 2, 1, 1, 1, 3) == True
    assert example3.intersect(0, 0, 5, 5, 1, 1, 3, 3) == True
    assert example3.intersect(1, 1, 3, 3, 2, 2, 2, 3) == True