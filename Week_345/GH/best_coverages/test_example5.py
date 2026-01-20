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
    assert example5.numerical_letter_grade([1.5]) == ["C-"]
    assert example5.numerical_letter_grade([1.2]) == ["D+"]
    assert example5.numerical_letter_grade([0.9]) == ["D"]
    assert example5.numerical_letter_grade([0.1]) == ["D-"]
    assert example5.numerical_letter_grade([0.0]) == ["E"]
    assert example5.numerical_letter_grade([-1]) == ["E"]
    assert example5.numerical_letter_grade([3.7, 2.9, 0.0]) == ["A", "B+", "E"]