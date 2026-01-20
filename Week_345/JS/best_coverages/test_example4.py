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
    # Test cases for choose_num function
    assert choose_num(4, 10) == 10  # 10 is the largest even number in the range
    assert choose_num(1, 7) == 6    # 6 is the largest even number in the range
    assert choose_num(7, 7) == -1    # No even number in the range
    assert choose_num(8, 8) == 8     # 8 is even and equals to x and y
    assert choose_num(5, 3) == -1    # x > y, should return -1
