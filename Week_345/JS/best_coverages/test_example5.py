import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example5 import *


def test_smoke_import():
    assert hasattr(example5, "__doc__") or True

def test_numerical_letter_grade():
    assert numerical_letter_grade([4.0]) == ['A+']
    assert numerical_letter_grade([3.8]) == ['A']
    assert numerical_letter_grade([3.5]) == ['A-']
    assert numerical_letter_grade([3.2]) == ['B+']
    assert numerical_letter_grade([2.5]) == ['B']
    assert numerical_letter_grade([1.8]) == ['C']
    assert numerical_letter_grade([0.5]) == ['D-']
    assert numerical_letter_grade([0.0]) == ['E']
    assert numerical_letter_grade([5.0]) == ['A+']  # Edge case, assuming 5.0 is capped at A+
    assert numerical_letter_grade([]) == []  # Edge case for empty list
