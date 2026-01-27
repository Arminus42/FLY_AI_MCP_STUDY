import sys
import os

# Setting up the path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example3 import *

def test_intersect_0():
    intersect(-2310, 101833, -12, 18, 886191, -1098984, 617241, -149996)

def test_intersect_1():
    intersect(999978, 32802, -1431669, -47, 607999, -1388524, -244021, 764800)

def test_intersect_2():
    intersect(-400018, -561126, 611989, 1507918, 275, 5175, -7416, -607610)

def test_intersect_3():
    intersect(1817981, 2110, 1417114, -1580126, -500172, -45, 211, -7)