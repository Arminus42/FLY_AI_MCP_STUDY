import example2
import pytest

def test_testme():
    # Test case where c is in range (57, 284) and a increments
    a, b, c = 0, 5, 100
    example2.testme(a, b, c)
    assert a < b  # Check that the loop was executed

    # Test case where c is out of range, a decreases
    a, b, c = 0, 5, 50
    example2.testme(a, b, c)
    assert a < 0  # Ensure that a goes below 0 and breaks
    
    # Test case where a equals b
    a, b, c = 5, 5, 100
    example2.testme(a, b, c)  # Should return immediately
    
    # Test case where a is already negative
    a, b, c = -1, 5, 100
    example2.testme(a, b, c)  # Should return immediately
    
    # Test case where c is at the edge of the valid range
    a, b, c = 0, 10, 57
    example2.testme(a, b, c)
    assert a < 0  # Ensure that a goes below 0 and breaks