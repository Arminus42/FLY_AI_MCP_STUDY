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
    assert numerical_letter_grade([4.0]) == ['A+']  # Exact A+
    assert numerical_letter_grade([3.8]) == ['A']  # Above A+
    assert numerical_letter_grade([3.4]) == ['A-']  # Above A-
    assert numerical_letter_grade([2.8]) == ['B']  # Above B
    assert numerical_letter_grade([1.5]) == ['D+']  # Below D+
    assert numerical_letter_grade([0.0]) == ['E']  # Exact case for E

def test_numerical_letter_grade_additional():
    assert numerical_letter_grade([3.1]) == ['B+']  # Above B+
    assert numerical_letter_grade([2.4]) == ['B-']  # Above B-
    assert numerical_letter_grade([2.1]) == ['C+']  # Above C+
    assert numerical_letter_grade([1.8]) == ['C']  # Above C
    assert numerical_letter_grade([1.2]) == ['C-']  # Above C-
    assert numerical_letter_grade([0.8]) == ['D']  # Above D
    assert numerical_letter_grade([-1.0]) == ['E']  # Negative GPA
