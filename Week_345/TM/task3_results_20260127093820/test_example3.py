import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example3 import *

def test_intersect_0():
    intersect(46, 755979, 1733550, 864352, 8, 22, -87, 93)

def test_intersect_1():
    intersect(-1894671, 98, 66, 51, 160, -90, 40, 797481)

def test_intersect_2():
    intersect(-100065, 1094536, -1930994, 7897, -999696, -690615, -955162, -1005838)

def test_intersect_3():
    intersect(1493893, -302761, -1457476, 1971, 1002795, 2058560, -1142184, -100054)
