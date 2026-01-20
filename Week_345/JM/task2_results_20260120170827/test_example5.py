import pytest
from example5 import numerical_letter_grade

def test_numerical_letter_grade():
    assert numerical_letter_grade([4.0]) == ['A+']
    assert numerical_letter_grade([3.8]) == ['A']
    assert numerical_letter_grade([3.4]) == ['A-']
    assert numerical_letter_grade([3.1]) == ['B+']
    assert numerical_letter_grade([2.8]) == ['B']
    assert numerical_letter_grade([2.4]) == ['B-']
    assert numerical_letter_grade([2.1]) == ['C+']
    assert numerical_letter_grade([1.8]) == ['C']
    assert numerical_letter_grade([1.4]) == ['C-']
    assert numerical_letter_grade([1.2]) == ['D+']
    assert numerical_letter_grade([0.8]) == ['D']
    assert numerical_letter_grade([0.1]) == ['D-']
    assert numerical_letter_grade([0.0]) == ['E']
    assert numerical_letter_grade([]) == [] # Edge case: empty list
    assert numerical_letter_grade([-1.0]) == ['E'] # Edge case: negative GPA
