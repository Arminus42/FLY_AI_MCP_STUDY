import pytest

from example3.example3 import intersect

def test_intersect_overlapping_lines():
    assert intersect(0, 0, 5, 5, 0, 0, 5, 5) == True

def test_intersect_non_overlapping_lines():
    assert intersect(0, 0, 1, 1, 2, 2, 3, 3) == False

def test_intersect_parallel_lines():
    assert intersect(0, 0, 1, 1, 0, 1, 1, 2) == False

def test_intersect_perpendicular_lines():
    assert intersect(0, 0, 0, 5, -5, 2, 5, 2) == True

def test_intersect_one_point_lines():
    assert intersect(0, 0, 1, 1, 1, 1, 2, 2) == True

def test_intersect_collinear_overlapping_lines():
    assert intersect(0, 0, 5, 0, 2, 0, 7, 0) == True

def test_intersect_collinear_non_overlapping_lines():
    assert intersect(0, 0, 1, 0, 2, 0, 3, 0) == False

def test_intersect_vertical_and_horizontal_lines():
    assert intersect(0, 0, 0, 5, -2, 2, 2, 2) == True

def test_intersect_vertical_and_horizontal_lines_no_intersection():
    assert intersect(0, 0, 0, 5, 1, 1, 1, 5) == False
