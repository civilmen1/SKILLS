"""Tests unitarios para cálculo sísmico NBDS-2023."""
from structural_skill.models import SeismicParams
from structural_skill.nbds2023 import design_spectrum, site_factors


def test_site_factors_S2():
    """Para suelo S2, fa=fb=1.0 (suelo de referencia)."""
    params = SeismicParams(So=0.35, soil_type="S2")
    fa, fb = site_factors(params)
    assert abs(fa - 1.0) < 0.01
    assert abs(fb - 1.0) < 0.01


def test_design_spectrum_positive():
    """Sa(T) debe ser positivo para cualquier T."""
    params = SeismicParams(So=0.35, soil_type="S2", R=4.0, importance_factor=1.0)
    for T in [0.0, 0.1, 0.5, 1.0, 2.0]:
        Sa = design_spectrum(params, T)
        assert Sa > 0, f"Sa({T}) = {Sa} no es positivo"


def test_design_spectrum_decreasing():
    """Sa(T) debe decrecer para T > Ts."""
    params = SeismicParams(So=0.35, soil_type="S2", R=4.0)
    Sa1 = design_spectrum(params, 0.5)
    Sa2 = design_spectrum(params, 1.5)
    assert Sa1 > Sa2
