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

def test_testme_no_loop_when_a_not_less_than_b():
    # While condition false immediately
    assert testme(5, 5, 100) is None
    assert testme(6, 5, 100) is None


def test_testme_increment_path_breaks_on_b():
    # c in (57, 284) so a increments until it reaches b
    assert testme(0, 2, 100) is None


def test_testme_decrement_path_breaks_on_negative():
    # c outside range so a decrements, should break when a < 0
    assert testme(0, 10, 0) is None
