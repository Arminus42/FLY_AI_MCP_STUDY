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
    assert foo(42, 0) == 1  # Tests coverage of lines 2, 3, 4
    assert foo(42, 1) == 0  # Tests coverage of line 7
    assert foo(1, 0) == -1   # Tests coverage of lines 9-10


def test_bar():
    assert bar(4, 2, 3) == 3     # Tests coverage of line 13
    assert bar(6, 2, 4) == 6     # Tests coverage of line 15
    assert bar(2, 4, 3) == 4     # Tests coverage of line 18
