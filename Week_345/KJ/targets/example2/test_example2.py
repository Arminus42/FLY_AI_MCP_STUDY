import pytest
from example2 import testme


def test_testme():
    assert testme(10, 20, 100) is None
    assert testme(10, 20, 300) is None
    assert testme(0, 10, 56) is None
    assert testme(10, 20, 50) is None
