import pytest

from example3 import intersect

class TestIntersect:

    def test_non_intersecting_lines(self):
        assert intersect(0, 0, 1, 1, 1, 0, 2, 1) == False

    def test_intersecting_lines(self):
        assert intersect(0, 0, 2, 2, 0, 2, 2, 0) == True

    def test_touching_lines(self):
        assert intersect(1, 1, 3, 3, 2, 2, 2, 2) == True

    def test_collinear_lines(self):
        assert intersect(0, 0, 2, 2, 1, 1, 3, 3) == True

    def test_parallel_lines(self):
        assert intersect(0, 0, 1, 1, 0, 1, 1, 2) == False

    def test_coincident_lines(self):
        assert intersect(0, 0, 2, 2, 0, 0, 1, 1) == True

    def test_edge_case_u1t_zero(self):
        assert intersect(0, 0, 1, 1, 1, 0, 1, 1) == True
    
    def test_edge_case_u2t_zero(self):
        assert intersect(0, 0, 1, 1, 0, 0, 2, 2) == True