import sys
import os

# Add the directory containing 'example2.py' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'targets', 'example2')))

import pytest
from example2 import *

def test_testme_0():
    testme(453272, -91549, 1957671)

def test_testme_1():
    testme(7780, 1507027, 1674)