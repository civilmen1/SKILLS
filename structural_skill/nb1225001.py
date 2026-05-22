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

    Convenio de unidades (consistente N-mm):
        Mu  [kN·m/m]  -> multiplicar por 1e6 para obtener [N·mm/m]
        b   [m]       -> multiplicar por 1000 para obtener [mm]
        d   [m]       -> multiplicar por 1000 para obtener [mm]
        fc, fy        [MPa = N/mm2]
        As resultado  [mm2/mm] -> dividir por 10 para obtener [cm2/m]

    Resuelve la ecuación cuadrática:
        phi*As*fy*(d - As*fy/(2*0.85*fc*b)) = Mu
    """
    Mu_Nmm = Mu * 1e6      # kN·m/m -> N·mm/m  (1 kN=1000 N, 1 m=1000 mm -> x1e6)
    b_mm = b * 1000        # m -> mm  (franja 1m = 1000 mm)
    d_mm = d * 1000        # m -> mm
    phi = PHI_FLEXION

    # Ecuación cuadrática: a_coef*As^2 - b_coef*As + c_coef = 0
    # donde As está en [mm2] (para franja de b_mm mm)
    a_coef = fy / (2.0 * 0.85 * fc * b_mm)
    b_coef = d_mm
    c_coef = Mu_Nmm / (phi * fy)

    discriminant = b_coef**2 - 4.0 * a_coef * c_coef
    if discriminant < 0:
        return float('inf')  # sección insuficiente

    As_mm2_per_bmm = (b_coef - math.sqrt(discriminant)) / (2.0 * a_coef)  # mm2 en franja b_mm
    # Convertir a cm2/m: As[mm2/mm] = As_mm2_per_bmm / b_mm; luego *100 cm2/m
    As_cm2_m = (As_mm2_per_bmm / b_mm) * 100.0
    return As_cm2_m


def MRd_slab(As: float, fc: float, fy: float, b: float, d: float) -> float:
    """
    Momento resistente de diseño de una losa [kN·m/m].

    Convenio de unidades (consistente N-mm):
        As  [cm2/m]  -> mm2/mm multiplicando por 100 y dividiendo por 1000
        b   [m]      -> mm
        d   [m]      -> mm
        Resultado    -> N·mm/mm -> dividir entre 1e3 para kN·m/m

    Args:
        As: Área de acero [cm2/m].
        d: Peralte efectivo [m].
    Returns:
        MRd [kN·m/m]
    """
    b_mm = b * 1000                   # m -> mm
    d_mm = d * 1000                   # m -> mm
    As_mm2_per_mm = As * 100 / 1000   # cm2/m -> mm2/mm
    As_mm2 = As_mm2_per_mm * b_mm     # mm2 total en franja b_mm

    a = As_mm2 * fy / (0.85 * fc * b_mm)          # profundidad bloque compresión [mm]
    MRd_Nmm = PHI_FLEXION * As_mm2 * fy * (d_mm - a / 2.0)   # N·mm (en franja b_mm)
    MRd_kNm_m = MRd_Nmm / b_mm / 1e3             # N·mm/mm -> kN·m/m
    return MRd_kNm_m


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


def check_deflection(L: float, h: float, support: str = "continuous") -> dict:
    """
    Verificación de flecha por relación L/h según NB 1225001.

    Límites NB 1225001:
        Losa simplemente apoyada:  L/h <= 20
        Losa continua:             L/h <= 28
        Losa en voladizo:          L/h <= 10
    """
    ratio = L / h
    limit_map = {"simple": 20, "continuous": 28, "cantilever": 10}
    limit = limit_map.get(support, 28)
    ok = ratio <= limit
    return {
        "L_h_ratio": round(ratio, 2),
        "L_h_limit": limit,
        "L_h_ok": ok,
        "norma": "NB 1225001 — Control de deflexiones L/h"
    }
