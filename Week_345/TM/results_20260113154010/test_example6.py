import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../targets/example6')))
import example6


def test_prod_signs():
    assert example6.prod_signs([1, -2, 3]) == 6   # 1 + 2 + 3 with product of signs = 1
    assert example6.prod_signs([-1, -2, -3]) == -6  # 1 + 2 + 3 with product of signs = -1
    assert example6.prod_signs([1, 0, 3]) == 4  # 1 + 0 + 3 with product of signs = 0
    assert example6.prod_signs([]) == None  # empty array
    assert example6.prod_signs([-1, 2, 0, -3]) == 6  # 1 + 2 + 3 with product of signs = 0
