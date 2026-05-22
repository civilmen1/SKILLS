"""Generación de reportes técnicos de diseño estructural."""
from structural_skill.models import SlabResult


def print_slab_report(result: SlabResult, project_name: str = "Proyecto") -> None:
    """Imprime un reporte de texto del resultado de optimización de losa."""
    sep = "=" * 60
    print(sep)
    print(f"  REPORTE DE DISEÑO DE LOSA — {project_name}")
    print(f"  NB 1225001 (2019/2020) + NBDS-2023")
    print(sep)
    print(f"  Espesor óptimo (h):        {result.h*100:.0f} cm")
    print(f"  Armadura principal:        Ø{result.bar_main}@{result.spacing_main*100:.0f}cm  ({result.As_main:.2f} cm2/m)")
    print(f"  Armadura distribución:     Ø{result.bar_dist}@{result.spacing_dist*100:.0f}cm  ({result.As_dist:.2f} cm2/m)")
    print(f"  Momento de diseño (Mu):    {result.Mu_design:.2f} kN·m/m")
    print(f"  Momento resistente (MRd):  {result.MRd:.2f} kN·m/m")
    print(sep)
    print("  VERIFICACIONES NORMATIVAS:")
    for k, v in result.checks.items():
        status = "✓" if v is True else ("✗" if v is False else f"{v}")
        print(f"    {k:<30} {status}")
    print(sep)
    if result.alternatives:
        print("  ALTERNATIVAS:")
        for i, alt in enumerate(result.alternatives, 1):
            print(f"    [{i}] h={alt['h']*100:.0f}cm  Ø{alt['bar']}@{alt['spacing']*100:.0f}cm  costo_idx={alt['cost']}")
    print(sep)


def slab_report_dict(result: SlabResult) -> dict:
    """Retorna el reporte como diccionario serializable (para JSON/API)."""
    return {
        "h_cm": result.h * 100,
        "armadura_principal": f"Ø{result.bar_main}@{result.spacing_main*100:.0f}cm",
        "As_main_cm2m": result.As_main,
        "armadura_distribucion": f"Ø{result.bar_dist}@{result.spacing_dist*100:.0f}cm",
        "As_dist_cm2m": result.As_dist,
        "Mu_kNm_m": result.Mu_design,
        "MRd_kNm_m": result.MRd,
        "checks": result.checks,
        "alternatives": result.alternatives,
        "cost_index": result.cost_index,
    }
