# test_example2.py
import sys
import os

# Adjust sys.path to include the directory of the target module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example2 import *

def test_testme_0():
    testme(28728, 86, 1989384)
