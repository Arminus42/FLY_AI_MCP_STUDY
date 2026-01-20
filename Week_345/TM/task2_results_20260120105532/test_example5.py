import pytest
from example5 import numerical_letter_grade


def test_numerical_letter_grade():
    # Test with various GPAs
    assert numerical_letter_grade([4.0]) == ['A+']
    assert numerical_letter_grade([3.8]) == ['A']
    assert numerical_letter_grade([3.4]) == ['A-']
    assert numerical_letter_grade([3.2]) == ['B+']
    assert numerical_letter_grade([2.8]) == ['B']
    assert numerical_letter_grade([2.4]) == ['B-']
    assert numerical_letter_grade([2.1]) == ['C+']
    assert numerical_letter_grade([1.8]) == ['C']
    assert numerical_letter_grade([1.5]) == ['C-']
    assert numerical_letter_grade([1.2]) == ['D+']
    assert numerical_letter_grade([0.8]) == ['D']
    assert numerical_letter_grade([0.5]) == ['D-']
    assert numerical_letter_grade([0.0]) == ['E']
    
    # Test with a list of GPAs
    assert numerical_letter_grade([4.0, 3.8, 3.5, 2.5, 1.5, 0.0]) == ['A+', 'A', 'A-', 'B-', 'C-', 'E']
    
    # Test with empty list
    assert numerical_letter_grade([]) == []
