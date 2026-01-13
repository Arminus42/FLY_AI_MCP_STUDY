import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/example3')))
import example3


def test_intersect():
    # Example test cases for intersect function
    assert example3.intersect(0, 0, 2, 2, 0, 2, 2, 0) == True  # lines intersect
    assert example3.intersect(0, 0, 1, 1, 2, 2, 3, 3) == False  # lines do not intersect
    assert example3.intersect(0, 0, 1, 1, 1, 0, 1, 2) == True  # endpoint intersection
    assert example3.intersect(0, 0, 0, 1, 0, 0, 0, 1) == True  # overlap
    assert example3.intersect(0, 0, 0, 1, 1, 0, 1, 1) == False  # separate lines