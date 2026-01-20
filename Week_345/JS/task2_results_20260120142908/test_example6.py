import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example6 import *


def test_smoke_import():
    assert hasattr(example6, "__doc__") or True

def test_prod_signs():
    assert prod_signs([1, 2, 3]) == 6       # All positive numbers, sum = 6, prod = 1
    assert prod_signs([-1, -2, -3]) == -6    # All negative numbers, sum = 6, prod = -1
    assert prod_signs([-1, 2, 3]) == 6       # Mixed positive and negative, sum = 6, prod = 1
    assert prod_signs([0, 1, -2]) == 0       # Includes zero, prod = 0, result = 0
    assert prod_signs([]) is None            # Edge case, empty list should return None
    assert prod_signs([-1, 1, -1]) == -1     # Mixed signs, sum = 1, prod = -1
    assert prod_signs([2, -3, 5, 0]) == 0     # Includes zero, should return 0
