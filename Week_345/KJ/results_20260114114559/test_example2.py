import pytest

from example2 import testme


def test_testme():
    # Test case 1: Normal case
    assert testme(1, 10, 100) is None
    
    # Test case 2: Edge case with c > 57
    assert testme(5, 10, 100) is None

    # Test case 3: Edge case with c < 57
    assert testme(5, 10, 50) is None

    # Test case 4: Edge case with c > 284
    assert testme(1, 10, 300) is None

    # Test case 5: a starts negative
    assert testme(-1, 10, 100) is None

    # Test case 6: a >= b
    assert testme(10, 10, 100) is None
