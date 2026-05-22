"""Tests del motor de optimización."""
from structural_skill.optimizer import exhaustive_search


def test_exhaustive_finds_optimal():
    """El motor debe encontrar el mínimo en un espacio simple."""
    space = {"x": [1, 2, 3, 4, 5]}

    def feasible_fn(p):
        return p["x"] >= 3, {"x_ok": p["x"] >= 3}

    def cost_fn(p):
        return p["x"]  # minimizar x, pero >= 3

    results = exhaustive_search(space, feasible_fn, cost_fn, n_alternatives=2)
    assert results[0].params["x"] == 3
    assert len(results) == 2


def test_exhaustive_no_feasible():
    """Sin solución factible, retorna lista vacía."""
    space = {"x": [1, 2]}

    def feasible_fn(p):
        return False, {}

    def cost_fn(p):
        return p["x"]

    results = exhaustive_search(space, feasible_fn, cost_fn)
    assert results == []
