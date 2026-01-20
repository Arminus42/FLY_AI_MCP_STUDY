
import pytest

from example5.example5 import numerical_letter_grade


def test_numerical_letter_grade_edge_cases():
    assert numerical_letter_grade([4.0]) == ["A+"]
    assert numerical_letter_grade([0.0]) == ["E"]
    assert numerical_letter_grade([3.7]) == ["A"]
    assert numerical_letter_grade([3.3]) == ["A-"]
    assert numerical_letter_grade([3.0]) == ["B+"]
    assert numerical_letter_grade([2.7]) == ["B"]
    assert numerical_letter_grade([2.3]) == ["B-"]
    assert numerical_letter_grade([2.0]) == ["C+"]
    assert numerical_letter_grade([1.7]) == ["C"]
    assert numerical_letter_grade([1.3]) == ["C-"]
    assert numerical_letter_grade([1.0]) == ["D+"]
    assert numerical_letter_grade([0.7]) == ["D"]
    assert numerical_letter_grade([0.1]) == ["D-"]

def test_numerical_letter_grade_normal_cases():
    assert numerical_letter_grade([3.8, 3.5, 3.1, 2.8, 2.5, 2.1, 1.8, 1.5, 1.1, 0.8, 0.5]) == ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-"]

def test_numerical_letter_grade_empty_list():
    assert numerical_letter_grade([]) == []

def test_numerical_letter_grade_mixed_cases():
    assert numerical_letter_grade([4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.7, 0.0, 0.1]) == ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "E", "D-"]
