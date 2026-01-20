import example2


def test_testme():
    assert example2.testme(5, 10, 60) is None  # c is within range 57 < c < 284
    assert example2.testme(5, 10, 30) is None  # c is outside range
    assert example2.testme(5, 10, 300) is None  # c is outside range
    assert example2.testme(5, 5, 60) is None  # a == b, should not enter the loop
    assert example2.testme(-1, 10, 60) is None  # a starts negative
    assert example2.testme(10, 10, 60) is None  # a == b, should not enter the loop
