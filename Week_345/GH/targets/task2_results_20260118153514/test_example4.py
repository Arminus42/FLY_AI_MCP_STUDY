import example4
import pytest

def test_choose_num():
    assert example4.choose_num(1, 10) == 10
    assert example4.choose_num(3, 7) == 6
    assert example4.choose_num(8, 8) == 8
    assert example4.choose_num(2, 5) == 4
    assert example4.choose_num(1, 1) == -1
    assert example4.choose_num(8, 9) == 8
    assert example4.choose_num(10, 15) == 14
    assert example4.choose_num(20, 15) == -1
    assert example4.choose_num(0, 10) == 10
    assert example4.choose_num(5, 5) == -1