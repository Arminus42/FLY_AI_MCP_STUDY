import sys
import os

# Add the target module path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example3 import *

def test_intersect_0():
    intersect(0, -95, 73, -310960, -8, 1349220, 80, -73)

def test_intersect_1():
    intersect(428289, 1727078, -48, -1752371, -4, -1887018, 52, 759348)

def test_intersect_2():
    intersect(-3270, -2100094, 6588, -50, -521, -999999, -280107, 7626)

def test_intersect_3():
    intersect(-1193191, -1112181, -1493511, 3, 31432, 87, -29, -90)
