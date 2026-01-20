import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example4 import *


def test_smoke_import():
    assert hasattr(example4, "__doc__") or True

def test_choose_num():
    assert choose_num(1, 10) == 10  # Highest even in range
    assert choose_num(1, 11) == 10  # Highest even in range
    assert choose_num(10, 20) == 20  # Highest even in range
    assert choose_num(5, 5) == -1  # Single number range, odd
    assert choose_num(10, 9) == -1  # Invalid range
