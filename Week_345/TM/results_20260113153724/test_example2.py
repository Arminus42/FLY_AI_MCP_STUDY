import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/example2')))
import example2

def test_testme():
    # Test cases for the testme function
    assert example2.testme(1, 10, 60) is None
    assert example2.testme(5, 5, 70) is None
    assert example2.testme(0, 10, 50) is None
    assert example2.testme(10, 20, 300) is None
    assert example2.testme(-1, 10, 100) is None
    # Add more assertions as needed