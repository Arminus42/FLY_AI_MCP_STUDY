import example5

def test_numerical_letter_grade():
    # Test case 1: Full range of GPA values
    assert example5.numerical_letter_grade([4.0, 3.9, 3.6, 3.4, 3.1, 2.8, 2.4, 2.1, 1.8, 1.4, 1.2, 0.5, 0.0]) == ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'E']
    
    # Test case 2: Edge case for exact matches
    assert example5.numerical_letter_grade([4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.7, 0.0]) == ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'E']
    
    # Test case 3: All failing grades
    assert example5.numerical_letter_grade([0.0, 0.0, 0.0]) == ['E', 'E', 'E']
    
    # Test case 4: All perfect grades
    assert example5.numerical_letter_grade([4.0, 4.0, 4.0]) == ['A+', 'A+', 'A+']
    
    # Test case 5: Mixed grades with some duplicates
    assert example5.numerical_letter_grade([4.0, 3.7, 3.7, 2.5, 3.3, 1.5, 0.5]) == ['A+', 'A', 'A', 'B-', 'A-', 'D+', 'E']