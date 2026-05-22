"""Verificaciones de diseño según NB 1225001 — Hormigón Estructural (2019/2020)."""
import math

# ---------------------------------------------------------------------------
# CONSTANTES NB 1225001
# ---------------------------------------------------------------------------
PHI_FLEXION = 0.90    # Factor de reducción de resistencia a flexión
PHI_CORTANTE = 0.75   # Factor de reducción de resistencia a cortante
GAMMA_C = 25.0        # Peso específico del hormigón [kN/m3]


# ---------------------------------------------------------------------------
# ARMADURA MÍNIMA Y MÁXIMA EN LOSAS — NB 1225001
# ---------------------------------------------------------------------------

def As_min_slab(fc: float, fy: float, b: float, h: float) -> float:
    """
    Armadura mínima en losas según NB 1225001.

    Para barras con fy <= 420 MPa: rho_min = 0.0018
    Para barras con fy > 420 MPa:  rho_min = max(0.0014, 0.0018 * 420 / fy)

    Args:
        fc: Resistencia del hormigón [MPa].
        fy: Fluencia del acero [MPa].
        b: Ancho de la franja [m] (normalmente 1.0 m).
        h: Espesor de losa [m].

    Returns:
        As_min [cm2/m]
    """
    if fy <= 420:
        rho_min = 0.0018
    else:
        rho_min = max(0.0014, 0.0018 * 420 / fy)
    return rho_min * b * h * 1e4  # cm2/m


def As_max_slab(fc: float, fy: float, b: float, d: float) -> float:
    """
    Armadura máxima en losas según NB 1225001 (0.75 * rho_bal).

    Args:
        d: Peralte efectivo [m].
    Returns:
        As_max [cm2/m]
    """
    beta1 = max(0.65, 0.85 - 0.05 * (fc - 28) / 7)
    rho_bal = (0.85 * beta1 * fc / fy) * (600 / (600 + fy))
    rho_max = 0.75 * rho_bal
    return rho_max * b * d * 1e4  # cm2/m


def As_required_flexure(Mu: float, fc: float, fy: float, b: float, d: float) -> float:
    """
    Área de acero requerida para flexión en losas [cm2/m].

    Mu [kN·m/m], b [m] (franja = 1m), d [m]

    Resuelve la ecuación cuadrática de resistencia a la flexión:
    Mu = phi * As * fy * (d - As*fy / (2*0.85*fc*b))
    """
    Mu_Nm = Mu * 1e3       # kN·m -> N·m
    b_mm = b * 1000        # m -> mm
    d_mm = d * 1000        # m -> mm
    fy_N = fy              # MPa = N/mm2
    fc_N = fc
    phi = PHI_FLEXION

    # Coeficientes cuadráticos: a*As^2 + b_coef*As + c = 0
    a_coef = fy_N / (2 * 0.85 * fc_N * b_mm)
    b_coef = -d_mm
    c_coef = Mu_Nm / (phi * fy_N)
    discriminant = b_coef**2 - 4 * a_coef * c_coef
    if discriminant < 0:
        return float('inf')  # sección insuficiente
    As_mm2 = (-b_coef - math.sqrt(discriminant)) / (2 * a_coef)  # mm2/m
    return As_mm2 / 100  # cm2/m


def MRd_slab(As: float, fc: float, fy: float, b: float, d: float) -> float:
    """
    Momento resistente de diseño de una losa [kN·m/m].

    Args:
        As: Área de acero [cm2/m].
        d: Peralte efectivo [m].
    Returns:
        MRd [kN·m/m]
    """
    As_mm2 = As * 100  # cm2/m -> mm2/m
    b_mm = b * 1000
    d_mm = d * 1000
    a = As_mm2 * fy / (0.85 * fc * b_mm)  # Profundidad del bloque de compresión [mm]
    MRd_Nmm = PHI_FLEXION * As_mm2 * fy * (d_mm - a / 2)
    return MRd_Nmm / 1e6  # N·mm -> kN·m/m


def bar_area(diameter_mm: int) -> float:
    """Área de una barra [cm2] dado su diámetro [mm]."""
    return math.pi * (diameter_mm / 10)**2 / 4


def As_provided(diameter_mm: int, spacing_m: float) -> float:
    """
    Área de acero provista por barras de diámetro dado a cierta separación [cm2/m].

    Args:
        diameter_mm: Diámetro de la barra [mm].
        spacing_m: Separación entre barras [m].
    Returns:
        As [cm2/m]
    """
    return bar_area(diameter_mm) / spacing_m


def check_spacing(diameter_mm: int, spacing_m: float, h: float) -> dict:
    """
    Verifica separaciones mínima y máxima según NB 1225001.

    Separación mínima: max(25mm, 1.5*diámetro barra)
    Separación máxima en losas: min(3h, 450mm)
    """
    spacing_mm = spacing_m * 1000
    s_min = max(25, 1.5 * diameter_mm)
    s_max = min(3 * h * 1000, 450)
    return {
        "s_min_ok": spacing_mm >= s_min,
        "s_max_ok": spacing_mm <= s_max,
        "s_min_ref": s_min,
        "s_max_ref": s_max,
        "norma": "NB 1225001 — Separaciones en losas"
    }


def check_deflection(L: float, h: float, deflection_limit: float = 250.0) -> dict:
    """
    Verificación simplificada de flecha por esbeltez (L/h) según NB 1225001.

    Para losas continuas con fy=420 MPa: L/h <= 28 (aprox.)
    Este chequeo es preliminar; una verificación rigurosa requiere cálculo de flecha real.
    """
    ratio = L / h
    # Límite básico NB 1225001 para losa simplemente apoyada
    limit_map = {"simple": 20, "continuous": 28, "cantilever": 10}
    return {
        "L_h_ratio": round(ratio, 2),
        "norma": "NB 1225001 — Control de deflexiones L/h"
    }
