"""Optimización de losas de hormigón armado según NB 1225001 y NBDS-2023."""
import math
import numpy as np
from structural_skill.models import (
    Materials, Loads, SeismicParams, SlabConstraints, SlabResult
)
from structural_skill.nb1225001 import (
    As_min_slab, As_max_slab, As_required_flexure,
    MRd_slab, As_provided, check_spacing, check_deflection, GAMMA_C
)
from structural_skill.nbds2023 import design_spectrum
from structural_skill.optimizer import exhaustive_search
from structural_skill.validators import (
    validate_materials, validate_loads, validate_seismic, validate_slab_constraints
)

# Coeficientes de carga última NB 1225001
LCF_D = 1.2   # Carga muerta
LCF_L = 1.6   # Carga viva


def _moment_coeff_one_way(support: str) -> tuple[float, float]:
    """
    Coeficientes de momento para losas unidireccionales.
    Retorna (Cm_neg, Cm_pos)  — fracción de wu*L^2.
    """
    coeff_map = {
        "simple":     (0.000, 0.125),
        "continuous":  (0.083, 0.063),
        "cantilever": (0.500, 0.000),
    }
    return coeff_map.get(support, (0.083, 0.063))


def _self_weight(h: float) -> float:
    """Peso propio de losa [kN/m2]."""
    return GAMMA_C * h


def optimize_slab(
    slab_type: str,
    spans: list[float],
    loads: dict,
    seismic: dict,
    materials: dict,
    constraints: dict,
    objective: str = "min_steel",
    support: str = "continuous",
) -> SlabResult:
    """
    Optimiza el espesor y armadura de una losa según NB 1225001 y NBDS-2023.

    Args:
        slab_type: "one_way" | "two_way"
        spans: Lista de luces [m]. Para one_way: [Lx]. Para two_way: [Lx, Ly].
        loads: {"dead": kN/m2, "live": kN/m2}
        seismic: {"So": g, "soil_type": "S2", "category": "C"}
        materials: {"fc": MPa, "fy": MPa, "cover": m (opt)}
        constraints: {"h_min": m, "h_max": m, "bar_diameters": [mm], "spacing": [m]}
        objective: "min_steel" | "min_concrete" | "min_cost"
        support: "simple" | "continuous" | "cantilever"

    Returns:
        SlabResult con la solución óptima y alternativas.
    """
    # --- Construcción de objetos ---
    mat = Materials(
        fc=materials["fc"],
        fy=materials["fy"],
        cover=materials.get("cover", 0.025),
    )
    lds = Loads(dead=loads["dead"], live=loads["live"])
    seis = SeismicParams(
        So=seismic["So"],
        soil_type=seismic.get("soil_type", "S2"),
        category=seismic.get("category", "C"),
        importance_factor=seismic.get("importance_factor", 1.0),
        R=seismic.get("R", 4.0),
    )
    constr = SlabConstraints(
        h_min=constraints["h_min"],
        h_max=constraints["h_max"],
        bar_diameters=constraints["bar_diameters"],
        spacing_options=constraints.get("spacing", [0.10, 0.125, 0.15, 0.20]),
    )

    # --- Validaciones ---
    errors = (
        validate_materials(mat)
        + validate_loads(lds)
        + validate_seismic(seis)
        + validate_slab_constraints(constr)
    )
    if errors:
        raise ValueError("Errores de validación:\n" + "\n".join(errors))

    L = spans[0]  # Luz principal [m]
    b = 1.0       # Franja de 1 m

    # --- Espacio de búsqueda ---
    h_range = np.arange(constr.h_min, constr.h_max + constr.h_step, constr.h_step)
    design_space = {
        "h": list(h_range),
        "bar": constr.bar_diameters,
        "spacing": constr.spacing_options,
    }

    # --- Función de factibilidad ---
    def feasibility_fn(params):
        h = params["h"]
        bar = params["bar"]
        spc = params["spacing"]
        d = h - mat.cover - (bar / 1000) / 2  # Peralte efectivo [m]
        if d <= 0:
            return False, {}

        # Cargas últimas
        sw = _self_weight(h)
        wu = LCF_D * (lds.dead + sw) + LCF_L * lds.live  # [kN/m2]

        # Momento de diseño
        Cm_neg, Cm_pos = _moment_coeff_one_way(support)
        Mu = max(Cm_neg, Cm_pos) * wu * L**2  # [kN·m/m]

        # Armadura requerida
        As_req = As_required_flexure(Mu, mat.fc, mat.fy, b, d)
        As_prov = As_provided(bar, spc)
        As_min = As_min_slab(mat.fc, mat.fy, b, h)
        As_max = As_max_slab(mat.fc, mat.fy, b, d)
        MRd = MRd_slab(As_prov, mat.fc, mat.fy, b, d)

        spacing_chk = check_spacing(bar, spc, h)
        defl_chk = check_deflection(L, h)

        checks = {
            "As_req": round(As_req, 3),
            "As_prov": round(As_prov, 3),
            "As_min": round(As_min, 3),
            "As_max": round(As_max, 3),
            "MRd": round(MRd, 3),
            "Mu": round(Mu, 3),
            "MRd >= Mu": MRd >= Mu,
            "As_prov >= As_req": As_prov >= As_req,
            "As_prov >= As_min": As_prov >= As_min,
            "As_prov <= As_max": As_prov <= As_max,
            **spacing_chk,
            **defl_chk,
        }
        feasible = (
            MRd >= Mu
            and As_prov >= As_req
            and As_prov >= As_min
            and As_prov <= As_max
            and spacing_chk["s_min_ok"]
            and spacing_chk["s_max_ok"]
        )
        return feasible, checks

    # --- Función de costo ---
    def cost_fn(params):
        h = params["h"]
        bar = params["bar"]
        spc = params["spacing"]
        As_prov = As_provided(bar, spc)
        if objective == "min_steel":
            return As_prov  # minimiza acero
        elif objective == "min_concrete":
            return h        # minimiza espesor
        else:  # min_cost
            return 1.2 * h + 0.01 * As_prov  # índice combinado

    # --- Búsqueda ---
    best_candidates = exhaustive_search(design_space, feasibility_fn, cost_fn, n_alternatives=3)

    if not best_candidates:
        raise RuntimeError(
            "No se encontró solución factible en el espacio de búsqueda. "
            "Amplíe el rango de espesor, diámetros o separaciones."
        )

    best = best_candidates[0]
    h_opt = best.params["h"]
    bar_opt = best.params["bar"]
    spc_opt = best.params["spacing"]
    d_opt = h_opt - mat.cover - (bar_opt / 1000) / 2
    sw = _self_weight(h_opt)
    wu = LCF_D * (lds.dead + sw) + LCF_L * lds.live
    Cm_neg, Cm_pos = _moment_coeff_one_way(support)
    Mu_opt = max(Cm_neg, Cm_pos) * wu * L**2

    # Armadura de distribución (temperatura/contracción) — misma barra, espac. * 1.5 aprox
    As_dist = As_min_slab(mat.fc, mat.fy, b, h_opt)
    bar_dist = bar_opt
    spacing_dist = min(constr.spacing_options, key=lambda s: abs(As_provided(bar_dist, s) - As_dist))

    alternatives = [
        {"h": c.params["h"], "bar": c.params["bar"], "spacing": c.params["spacing"],
         "cost": round(c.cost, 4)}
        for c in best_candidates[1:]
    ]

    return SlabResult(
        h=round(h_opt, 3),
        As_main=round(As_provided(bar_opt, spc_opt), 3),
        As_dist=round(As_dist, 3),
        bar_main=bar_opt,
        bar_dist=bar_dist,
        spacing_main=spc_opt,
        spacing_dist=spacing_dist,
        Mu_design=round(Mu_opt, 3),
        MRd=round(best.checks["MRd"], 3),
        checks=best.checks,
        alternatives=alternatives,
        cost_index=round(best.cost, 4),
    )
