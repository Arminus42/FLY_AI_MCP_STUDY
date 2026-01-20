import example3

def test_intersect_lines():
    # Test lines that intersect
    assert example3.intersect(1, 1, 4, 4, 1, 4, 4, 1) == True
    # Test lines that do not intersect (collinear but not overlapping)
    assert example3.intersect(1, 1, 4, 4, 1, 2, 4, 2) == False  # They are parallel and non-overlapping
    # Test overlapping lines
    assert example3.intersect(1, 1, 4, 4, 1, 1, 4, 4) == True  
    # Test touching lines
    assert example3.intersect(1, 1, 4, 4, 4, 1, 1, 4) == True  
    # Test vertical and horizontal lines
    assert example3.intersect(1, 1, 1, 4, 0, 2, 4, 2) == True  
    # Test parallel lines (they should not intersect)
    assert example3.intersect(1, 1, 4, 1, 1, 2, 4, 2) == False  
    # Edge case where lines start at the same point
    assert example3.intersect(1, 1, 1, 1, 1, 1, 1, 1) == True  
    # Test case where lines are vertical (but parallel so they do not intersect)
    assert example3.intersect(1, 1, 1, 4, 2, 1, 2, 4) == False  
    # Test case where lines are horizontal (but parallel so they do not intersect)
    assert example3.intersect(1, 1, 4, 1, 1, 2, 4, 2) == False  
    # Test for edge cases for u1t == 0
    assert example3.intersect(1, 1, 1, 5, 1, 2, 3, 4) == True  
    # Test special case where u2t is 0 (they are overlapping)
    assert example3.intersect(1, 1, 4, 4, 2, 2, 5, 5) == True  

def test_special_cases():
    # Case where u2 == 0 and u1t == 0, lines overlapping at (1,1)
    assert example3.intersect(0, 0, 2, 2, 1, 1, 3, 3) == True  
    # Parallel lines that do not intersect
    assert example3.intersect(0, 0, 0, 1, 1, 1, 3, 1) == False  
    # Collinear but not overlapping
    assert example3.intersect(1, 1, 5, 1, 2, 1, 4, 1) == False  
    # Vertical parallel lines that don't overlap
    assert example3.intersect(1, 1, 1, 5, 2, 2, 2, 3) == False  
    # Overlapping with both conditions true
    assert example3.intersect(0, 0, 0, 2, 0, 1, 0, 1) == True  
    # Collinear but one line contained within the other
    assert example3.intersect(1, 1, 4, 1, 2, 1, 3, 1) == True  # This tests fully contained lines

# Additional test for parallel lines 
def test_parallel_cases():
    assert example3.intersect(1, 1, 4, 1, 1, 2, 4, 2) == False  # Horizontal and parallel
    assert example3.intersect(2, 1, 2, 5, 2, 2, 2, 6) == False  # Vertical and parallel
