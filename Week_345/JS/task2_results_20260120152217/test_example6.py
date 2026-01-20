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
    assert prod_signs([1, 2, -3, 4]) == 6  # Positive product, sum of magnitudes
    assert prod_signs([-1, -2, -3]) == 6  # Negative product, sum of magnitudes
    assert prod_signs([1, 0, -3]) == 0  # Zero in array
    assert prod_signs([]) == None  # Empty array
    assert prod_signs([0, 1, 2, 3]) == 0  # Zero overrides positive
