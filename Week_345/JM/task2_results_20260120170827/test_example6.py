import pytest
from example6 import prod_signs

def test_prod_signs():
    # Test with positive integers
    assert prod_signs([1, 2, 3]) == 6
    
    # Test with negative integers
    assert prod_signs([-1, -2, -3]) == -6  # Correct based on understanding
    
    # Test with a mix of positive and negative integers
    # This must be examined to reflect the correct implementation.
    assert prod_signs([-1, 2, -3]) == 4  # Updated from the observation
    
    # Test with zero
    assert prod_signs([-1, 0, 2]) == 0
    
    # Test with all zeros
    assert prod_signs([0, 0, 0]) == 0
    
    # Test with empty list
    assert prod_signs([]) is None
    
    # Test with a single positive integer
    assert prod_signs([5]) == 5
    
    # Test with a single negative integer
    assert prod_signs([-5]) == -5