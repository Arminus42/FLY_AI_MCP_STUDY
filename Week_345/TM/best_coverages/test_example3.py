import pytest
from example3 import intersect

class TestIntersect:

    def test_non_intersecting_lines(self):
        assert intersect(0, 0, 2, 2, 3, 3, 5, 5) == False
        assert intersect(0, 0, 1, 1, 1, 0, 0, 1) == False

    def test_intersecting_lines(self):
        assert intersect(0, 0, 1, 1, 0, 1, 1, 0) == True
        assert intersect(0, 0, 1, 1, 1, 0, 0, 1) == True

    def test_collinear_lines(self):
        assert intersect(0, 0, 2, 2, 0, 0, 2, 2) == True
        assert intersect(0, 0, 0, 1, 0, 0, 0, 1) == True

    def test_vertical_lines(self):
        assert intersect(1, 0, 1, 1, 0, 0, 1, 0) == False
        assert intersect(1, 0, 1, 1, 1, 0, 1, 1) == True

    def test_horizontal_lines(self):
        assert intersect(0, 1, 2, 1, 0, 0, 2, 0) == False
        assert intersect(0, 1, 2, 1, 0, 1, 2, 1) == True