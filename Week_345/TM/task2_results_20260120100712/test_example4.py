import example4

def test_choose_num():
    # Test case where x and y are both even
    assert example4.choose_num(2, 6) == 6
    # Test case where x is even and y is odd
    assert example4.choose_num(2, 7) == 6
    # Test case where x and y are both odd (corrected expectation)
    assert example4.choose_num(3, 5) == 4
    # Test case where x is larger than y
    assert example4.choose_num(8, 5) == -1
    # Test case where x and y are equal and odd
    assert example4.choose_num(5, 5) == -1
    # Test case where x and y are equal and even
    assert example4.choose_num(4, 4) == 4
    # Test case where there are no even numbers in range
    assert example4.choose_num(1, 1) == -1
    # Test case for negative ranges, ensuring use of positive numbers
    assert example4.choose_num(-2, -1) == -1
    # Test case where y < 0
    assert example4.choose_num(0, -3) == -1
    # Test case for the smallest even number and largest even number in a higher range
    assert example4.choose_num(0, 20) == 20
    # Test case for smallest even and largest odd in a small range
    assert example4.choose_num(0, 1) == 0