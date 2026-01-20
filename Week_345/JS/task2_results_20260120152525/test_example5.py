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

def test_numerical_letter_grade_all_thresholds_and_edges():
    grades = [
        4.0,
        3.71, 3.7,
        3.31, 3.3,
        3.01, 3.0,
        2.71, 2.7,
        2.31, 2.3,
        2.01, 2.0,
        1.71, 1.7,
        1.31, 1.3,
        1.01, 1.0,
        0.71, 0.7,
        0.01, 0.0,
    ]

    assert numerical_letter_grade(grades) == [
        "A+",
        "A", "A-",
        "A-", "B+",
        "B+", "B",
        "B", "B-",
        "B-", "C+",
        "C+", "C",
        "C", "C-",
        "C-", "D+",
        "D+", "D",
        "D", "D-",
        "D-", "E",
    ]


def test_numerical_letter_grade_empty_list():
    assert numerical_letter_grade([]) == []
