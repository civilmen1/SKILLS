"""Tests unitarios para verificaciones NB 1225001."""
import pytest
from structural_skill.nb1225001 import (
    As_min_slab, As_max_slab, As_required_flexure, MRd_slab,
    As_provided, check_spacing, bar_area
)


def test_As_min_fy420():
    """rho_min = 0.0018 para fy=420 MPa."""
    As = As_min_slab(fc=21, fy=420, b=1.0, h=0.15)
    assert abs(As - 0.0018 * 1.0 * 0.15 * 1e4) < 0.01


def test_As_min_fy500():
    """rho_min reducido para fy > 420 MPa."""
    As = As_min_slab(fc=21, fy=500, b=1.0, h=0.15)
    expected_rho = max(0.0014, 0.0018 * 420 / 500)
    assert abs(As - expected_rho * 1.0 * 0.15 * 1e4) < 0.01


def test_bar_area_phi12():
    """Área de barra Ø12 = pi/4 * 1.2^2 cm2."""
    import math
    expected = math.pi * 1.44 / 4
    assert abs(bar_area(12) - expected) < 0.001


def test_MRd_exceeds_Mu():
    """El MRd de la sección con As provista debe ser >= Mu."""
    Mu = 15.0  # kN·m/m
    As_req = As_required_flexure(Mu, fc=21, fy=420, b=1.0, d=0.125)
    MRd = MRd_slab(As_req, fc=21, fy=420, b=1.0, d=0.125)
    assert MRd >= Mu * 0.99  # tolerancia numérica


def test_check_spacing_ok():
    chk = check_spacing(diameter_mm=12, spacing_m=0.15, h=0.15)
    assert chk["s_min_ok"] is True
    assert chk["s_max_ok"] is True


def test_As_provided():
    As = As_provided(diameter_mm=12, spacing_m=0.15)
    expected = bar_area(12) / 0.15
    assert abs(As - expected) < 0.001
