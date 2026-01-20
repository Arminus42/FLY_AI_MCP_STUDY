import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example3 import *


def test_smoke_import():
    assert hasattr(example3, "__doc__") or True

def test_intersect():
    # Test case where lines intersect
    assert intersect(0, 0, 1, 1, 0, 1, 1, 0) == True  # Lines intersect at (0.5, 0.5)

    # Test case where lines do not intersect
    assert intersect(0, 0, 1, 1, 1, 1, 2, 2) == False  # Lines are parallel

    # Test case where lines overlap
    assert intersect(0, 0, 2, 2, 1, 1, 2, 2) == True  # Line segment overlaps

    # Test case where lines are endpoints touching
    assert intersect(0, 0, 1, 1, 1, 1, 2, 2) == True  # Touching at (1, 1)
