import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example2 import *

def test_testme_0():
    testme(-502150, -504626, 999838)

def test_testme_1():
    testme(2, 283216, 135)
