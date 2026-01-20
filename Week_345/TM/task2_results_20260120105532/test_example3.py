import pytest
from example3 import intersect

class TestIntersect:

    def test_non_intersecting_lines(self):
        # lines that do not intersect
        assert intersect(0, 0, 2, 2, 3, 3, 5, 5) == False
        assert intersect(0, 0, 1, 1, 1, 2, 0, 1) == False

    def test_intersecting_lines(self):
        # lines that intersect
        assert intersect(0, 0, 1, 1, 0, 1, 1, 0) == True
        assert intersect(0, 0, 1, 1, 1, 0, 0, 1) == True

    def test_collinear_lines(self):
        # lines that are collinear and can overlap
        assert intersect(0, 0, 2, 2, 1, 1, 3, 3) == True  # line overlaps
        assert intersect(0, 0, 0, 1, 0, 0, 0, 1) == True  # overlapping

    def test_vertical_lines(self):
        # vertical lines that do and do not intersect
        assert intersect(1, 0, 1, 1, 1, 0, 1, 1) == True  # same line
        assert intersect(1, 0, 1, 1, 1, 2, 1, 3) == False  # parallel

    def test_horizontal_lines(self):
        # horizontal lines that do and do not intersect
        assert intersect(0, 1, 2, 1, 0, 0, 2, 0) == False  # parallel
        assert intersect(0, 1, 2, 1, 1, 1, 1, 1) == True  # same line