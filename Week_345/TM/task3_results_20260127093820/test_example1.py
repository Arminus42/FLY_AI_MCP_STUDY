import sys
import os

# Set up the path to the target module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from example1 import *

def test_foo_0():
    foo(42, -1698978)

def test_foo_1():
    foo(42, 0)

def test_bar_2():
    bar(499936, -100062, 257671)

def test_bar_3():
    bar(-22, 6655, 90505)
