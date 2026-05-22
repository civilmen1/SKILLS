"""Cálculo sísmico según Norma Boliviana de Diseño Sísmico NBDS-2023."""
import math
from structural_skill.models import SeismicParams

# Factores de amplificación de sitio fa y fb según NBDS-2023
# Tabla interpolada: {soil_type: {So_range: (fa, fb)}}
_FA = {
    "S1": {0.10: 0.8, 0.20: 0.8, 0.30: 0.8, 0.40: 0.8, 0.50: 0.8},
    "S2": {0.10: 1.0, 0.20: 1.0, 0.30: 1.0, 0.40: 1.0, 0.50: 1.0},
    "S3": {0.10: 1.2, 0.20: 1.2, 0.30: 1.1, 0.40: 1.0, 0.50: 1.0},
    "S4": {0.10: 1.6, 0.20: 1.4, 0.30: 1.2, 0.40: 1.1, 0.50: 1.0},
}
_FB = {
    "S1": {0.10: 0.8, 0.20: 0.8, 0.30: 0.8, 0.40: 0.8, 0.50: 0.8},
    "S2": {0.10: 1.0, 0.20: 1.0, 0.30: 1.0, 0.40: 1.0, 0.50: 1.0},
    "S3": {0.10: 1.7, 0.20: 1.6, 0.30: 1.5, 0.40: 1.4, 0.50: 1.3},
    "S4": {0.10: 2.4, 0.20: 2.0, 0.30: 1.8, 0.40: 1.6, 0.50: 1.5},
}


def _interp_factor(table: dict, soil_type: str, So: float) -> float:
    """Interpola un factor de sitio en función de So."""
    keys = sorted(table[soil_type].keys())
    vals = [table[soil_type][k] for k in keys]
    return float(np.interp(So, keys, vals))


def site_factors(params: SeismicParams) -> tuple[float, float]:
    """Devuelve (fa, fb) según tipo de suelo y So."""
    import numpy as np  # local para evitar importación circular si se usa standalone
    fa = float(np.interp(params.So, sorted(_FA[params.soil_type].keys()),
                         [_FA[params.soil_type][k] for k in sorted(_FA[params.soil_type].keys())]))
    fb = float(np.interp(params.So, sorted(_FB[params.soil_type].keys()),
                         [_FB[params.soil_type][k] for k in sorted(_FB[params.soil_type].keys())]))
    return fa, fb


def design_spectrum(params: SeismicParams, T: float) -> float:
    """
    Devuelve la aceleración espectral de diseño Sa(T) [g] según NBDS-2023.

    Args:
        params: Parámetros sísmicos del sitio.
        T: Período estructural [s].

    Returns:
        Sa [g] — aceleración espectral de diseño.
    """
    fa, fb = site_factors(params)
    Sms = fa * params.So          # Aceleración espectral corta (T=0.2s)
    Sm1 = fb * params.So          # Aceleración espectral a 1s
    Ts = Sm1 / Sms if Sms > 0 else 0.5
    T0 = 0.2 * Ts

    if T <= T0:
        Sa_e = Sms * (0.4 + 0.6 * T / T0)
    elif T <= Ts:
        Sa_e = Sms
    elif T <= 4.0:
        Sa_e = Sm1 / T
    else:
        Sa_e = Sm1 / T  # Extrapolación conservadora

    # Reducción por ductilidad
    Sa_d = Sa_e * params.importance_factor / params.R
    return Sa_d


def seismic_base_shear(params: SeismicParams, W: float, T: float) -> float:
    """
    Cortante basal sísmico simplificado V = Sa(T) * W [kN].

    Args:
        params: Parámetros sísmicos.
        W: Peso sísmico total [kN].
        T: Período fundamental estimado [s].

    Returns:
        V [kN]
    """
    return design_spectrum(params, T) * W
