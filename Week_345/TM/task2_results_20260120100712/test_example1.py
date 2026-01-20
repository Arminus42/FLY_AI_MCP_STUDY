import example1

def test_foo_42_0():
    assert example1.foo(42, 0) == 1

def test_foo_42_non_zero():
    assert example1.foo(42, 1) == 0

def test_foo_not_42():
    assert example1.foo(0, 0) == -1


def test_bar_avg_greater_than_z():
    assert example1.bar(30, 10, 15) == 30

def test_bar_avg_less_than_z_and_x_greater_than_y():
    assert example1.bar(10, 5, 8) == 10

def test_bar_else_case():
    assert example1.bar(5, 10, 8) == 10


def test_bar_avg_equal_to_z():
    assert example1.bar(10, 20, 15) == 20
