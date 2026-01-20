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

def test_foo():
    assert foo(42, 0) == 1  # First condition
    assert foo(42, 1) == 0  # Second condition
    assert foo(41, 0) == -1  # Else case
    assert foo(41, 1) == -1  # Else case

def test_bar():
    assert bar(10, 20, 5) == 5  # Average greater than z
    assert bar(30, 20, 15) == 30  # Average less than z, x > y
    assert bar(10, 20, 25) == 20  # Default case (non-conditional)

def test_bar_additional():
    assert bar(11, 10, 7) == 11  # Average less than z, x > y
    assert bar(15, 15, 10) == 15  # Average equal to z (non-conditional)
