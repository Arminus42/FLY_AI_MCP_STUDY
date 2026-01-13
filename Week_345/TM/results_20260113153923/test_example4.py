import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/example4')))
import example4

def test_choose_num():
    assert example4.choose_num(3, 9) == 8
    assert example4.choose_num(10, 20) == 20
    assert example4.choose_num(1, 1) == -1
    assert example4.choose_num(5, 5) == -1
    assert example4.choose_num(2, 4) == 4
    assert example4.choose_num(7, 12) == 12
    assert example4.choose_num(15, 10) == -1  # x > y