import example6


def test_prod_signs_with_positive_integers():
    assert example6.prod_signs([1, 2, 3]) == 6


def test_prod_signs_with_negative_integers():
    assert example6.prod_signs([-1, -2, -3]) == -6


def test_prod_signs_with_mixed_integers():
    assert example6.prod_signs([-1, 2, -3]) == 6


def test_prod_signs_with_zero():
    assert example6.prod_signs([0, 2, 3]) == 0


def test_prod_signs_with_empty_array():
    assert example6.prod_signs([]) is None


def test_prod_signs_with_non_zero_sum_and_negative_product():
    assert example6.prod_signs([-1, -1, 1]) == -1


def test_prod_signs_with_non_zero_sum_and_positive_product():
    assert example6.prod_signs([1, 1, -1]) == 1
