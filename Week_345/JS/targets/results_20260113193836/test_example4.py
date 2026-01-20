
from example4.example4 import choose_num

def test_choose_num():
    assert choose_num(2, 10) == 10
    assert choose_num(3, 9) == 8
    assert choose_num(10, 10) == -1
    assert choose_num(10, 12) == 12
    assert choose_num(11, 11) == -1
    assert choose_num(1, 5) == 4
    assert choose_num(1, 1) == -1
    assert choose_num(7, 7) == -1
    assert choose_num(8, 8) == 8
    assert choose_num(2, 1) == -1
    assert choose_num(10, 11) == 10

