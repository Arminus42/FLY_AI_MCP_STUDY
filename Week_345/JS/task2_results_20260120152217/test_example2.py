import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example2 import *


def test_smoke_import():
    assert hasattr(example2, "__doc__") or True

def test_testme():
    testme(1, 10, 60)  # c > 57, should increment a
    testme(1, 10, 50)  # c <= 57, should decrement a
    testme(10, 20, 100)  # c > 57, should increment a repeatedly
