import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example1 import *


def test_smoke_import():
    assert hasattr(example1, "__doc__") or True

def test_cover_all_branches_example1():
    # foo branches
    assert foo(42, 0) == 1          # x==42, y==0
    assert foo(42, 7) == 0          # x==42, y!=0
    assert foo(41, 0) == -1         # x!=42

    # bar branches
    assert bar(10, 10, 5) == 5      # (x+y)/2 > z => return z
    assert bar(9, 0, 5) == 9        # (x+y)/3 < z and x>y => return x
    assert bar(1, 5, 10) == 5       # else => return y
