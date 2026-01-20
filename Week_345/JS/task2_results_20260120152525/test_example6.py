import os
import sys
import pytest

# Dynamic path setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
TARGETS_DIR = os.path.join(PROJECT_ROOT, "targets")

if TARGETS_DIR not in sys.path:
    sys.path.insert(0, TARGETS_DIR)

from example6 import *


def test_smoke_import():
    assert hasattr(example6, "__doc__") or True

def test_prod_signs_empty_returns_none():
    assert prod_signs([]) is None


def test_prod_signs_contains_zero_results_zero():
    # Any zero forces prod to 0
    assert prod_signs([1, -2, 0, 4]) == 0


def test_prod_signs_all_positive():
    # prod = 1, sum abs = 1+2+3 = 6
    assert prod_signs([1, 2, 3]) == 6


def test_prod_signs_odd_number_of_negatives():
    # negatives count = 1 => prod = -1
    # sum abs = 1+2+3 = 6 => result -6
    assert prod_signs([-1, 2, 3]) == -6


def test_prod_signs_even_number_of_negatives():
    # negatives count = 2 => prod = 1
    # sum abs = 1+2+3 = 6
    assert prod_signs([-1, -2, 3]) == 6
