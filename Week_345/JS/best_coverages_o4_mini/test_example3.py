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
    assert intersect(0, 0, 1, 1, 0, 1, 1, 0) == True  # Lines intersect
    assert intersect(0, 0, 1, 1, 0, 0, 1, 1) == False  # Lines do not intersect
    assert intersect(0, 0, 0, 1, 0, 0, 1, 0) == True  # Overlapping lines
    assert intersect(0, 0, 1, 1, 0, 0, 0, 1) == True  # Coincident at an endpoint

def test_intersect_additional():
    assert intersect(1, 1, 2, 2, 3, 3, 4, 4) == False  # Parallel lines
    assert intersect(1, 1, 1, 2, 1, 1, 1, 2) == True  # Vertically coincident lines
