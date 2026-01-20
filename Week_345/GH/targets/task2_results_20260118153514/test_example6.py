import example6

def test_prod_signs():
    assert example6.prod_signs([1, -2, 3]) == 4
    assert example6.prod_signs([-1, -2, -3]) == -6
    assert example6.prod_signs([0, 2, 3]) == 0
    assert example6.prod_signs([1, 2, 3]) == 6
    assert example6.prod_signs([]) is None
    assert example6.prod_signs([-1, 0, 2]) == 0
    assert example6.prod_signs([0]) == 0
    assert example6.prod_signs([-1, 2, -3]) == -4