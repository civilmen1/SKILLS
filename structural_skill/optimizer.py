"""Motor de optimización discreta para secciones y armaduras."""
from dataclasses import dataclass
from typing import Callable
import itertools


@dataclass
class Candidate:
    """Candidato de diseño para evaluación."""
    params: dict       # Variables de diseño (h, bar, spacing, ...)
    feasible: bool     # Cumple todos los chequeos normativos
    checks: dict       # Resultados de verificaciones
    cost: float        # Función objetivo


def exhaustive_search(
    design_space: dict[str, list],
    feasibility_fn: Callable[[dict], tuple[bool, dict]],
    cost_fn: Callable[[dict], float],
    n_alternatives: int = 3,
) -> list[Candidate]:
    """
    Búsqueda exhaustiva discreta sobre el espacio de diseño.

    Args:
        design_space: Diccionario {variable: [opciones]}.
        feasibility_fn: Función que recibe un candidato dict y retorna (bool, checks_dict).
        cost_fn: Función que recibe un candidato dict y retorna float (costo).
        n_alternatives: Número de soluciones factibles a retornar, ordenadas por costo.

    Returns:
        Lista de Candidate ordenados por costo (mejor primero).
    """
    keys = list(design_space.keys())
    options = [design_space[k] for k in keys]
    candidates: list[Candidate] = []

    for combo in itertools.product(*options):
        params = dict(zip(keys, combo))
        feasible, checks = feasibility_fn(params)
        cost = cost_fn(params) if feasible else float('inf')
        candidates.append(Candidate(params=params, feasible=feasible, checks=checks, cost=cost))

    feasible_candidates = [c for c in candidates if c.feasible]
    feasible_candidates.sort(key=lambda c: c.cost)
    return feasible_candidates[:n_alternatives]
