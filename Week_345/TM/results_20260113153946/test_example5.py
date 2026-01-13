import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/example5')))

import example5

def test_numerical_letter_grade():
    assert example5.numerical_letter_grade([4.0]) == ["A+"]
    assert example5.numerical_letter_grade([3.8]) == ["A"]
    assert example5.numerical_letter_grade([3.4]) == ["A-"]
    assert example5.numerical_letter_grade([3.2]) == ["B+"]
    assert example5.numerical_letter_grade([2.8]) == ["B"]
    assert example5.numerical_letter_grade([2.4]) == ["B-"]
    assert example5.numerical_letter_grade([2.1]) == ["C+"]
    assert example5.numerical_letter_grade([1.8]) == ["C"]
    assert example5.numerical_letter_grade([1.4]) == ["C-"]
    assert example5.numerical_letter_grade([1.2]) == ["D+"]
    assert example5.numerical_letter_grade([0.8]) == ["D"]
    assert example5.numerical_letter_grade([0.2]) == ["D-"]
    assert example5.numerical_letter_grade([0.0]) == ["E"]
    
    # Test multiple GPAs
    assert example5.numerical_letter_grade([4.0, 3.8, 3.4, 2.1]) == ["A+", "A", "A-", "C+"]
