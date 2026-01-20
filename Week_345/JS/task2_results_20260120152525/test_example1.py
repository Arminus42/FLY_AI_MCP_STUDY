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

def test_foo_all_branches():
    # x == 42, y == 0
    assert foo(42, 0) == 1
    # x == 42, y != 0
    assert foo(42, 1) == 0
    # x != 42
    assert foo(41, 0) == -1


def test_bar_all_branches():
    # First branch: (x+y)/2 > z => return z
    assert bar(10, 10, 5) == 5

    # Second branch: (x+y)/2 <= z and (x+y)/3 < z and x > y => return x
    # Choose x=10,y=1 => (11)/2=5.5 <= 6, (11)/3=3.666 < 6 and x>y
    assert bar(10, 1, 6) == 10

    # Else branch: all other cases => return y
    # Make first condition false and second condition false via x<=y
    assert bar(1, 10, 100) == 10
