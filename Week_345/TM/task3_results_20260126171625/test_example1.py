import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example1 import *

def test_foo_0():
    foo(42, -1861)

def test_foo_1():
    foo(42, 0)

def test_bar_2():
    bar(1472402, -285097, -694015)

def test_bar_3():
    bar(-502396, 4094510, 2007191)
