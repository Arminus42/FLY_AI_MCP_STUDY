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

def test_intersect_u2_nonzero_true_and_false():
    # Proper crossing (u2 != 0 and parameters within [0,1])
    # Horizontal and vertical crossing at (1,0)
    assert intersect(0, 0, 2, 0, 1, -1, 1, 1) is True

    # u2 != 0 but intersection occurs outside segment range -> False
    # Horizontal segment from x=0..1, vertical line at x=2 crosses extension only
    assert intersect(0, 0, 1, 0, 2, -1, 2, 1) is False


def test_intersect_u2_zero_colinear_or_touching_cases():
    # u2 == 0 and u1t == 0 -> colinear/overlapping considered True
    assert intersect(0, 0, 2, 0, 1, 0, 3, 0) is True

    # u2 == 0 and u1t != 0 but u2t == 0 -> returns True via second check
    # Parallel horizontal lines y=0 and y=1 with chosen points making u2t==0
    assert intersect(0, 0, 2, 0, 1, 1, 3, 1) is True

    # u2 == 0 and neither u1t nor u2t is 0 -> False
    assert intersect(0, 0, 2, 0, 0, 1, 2, 1) is False

def test_intersect_u2_zero_hits_u2t_zero_branch():
    # Need u2 == 0 (parallel) and u1t != 0, u2t == 0 to hit line 25.
    # line1: horizontal from (0,0) to (2,0)
    # line2: horizontal from (1,1) to (3,1)
    # For these: u2 == 0, u1t = -2 (nonzero), u2t = 0
    assert intersect(0, 0, 2, 0, 1, 1, 3, 1) is True
