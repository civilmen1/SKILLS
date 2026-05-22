"""Ejemplo de optimización de losa unidireccional."""
from structural_skill.slabs import optimize_slab
from structural_skill.reports import print_slab_report

result = optimize_slab(
    slab_type="one_way",
    spans=[4.5],           # Luz de 4.5 m
    loads={
        "dead": 3.5,       # kN/m2 (acabados + tabiquería)
        "live": 2.0        # kN/m2 (vivienda)
    },
    seismic={
        "So": 0.35,        # Aceleración pico Cochabamba (aprox)
        "soil_type": "S2",
        "category": "C",
        "R": 4.0
    },
    materials={
        "fc": 21,          # MPa (H-210)
        "fy": 420,         # MPa
        "cover": 0.025     # 2.5 cm
    },
    constraints={
        "h_min": 0.12,
        "h_max": 0.22,
        "bar_diameters": [8, 10, 12],
        "spacing": [0.10, 0.125, 0.15, 0.175, 0.20]
    },
    objective="min_steel",
    support="continuous"
)

print_slab_report(result, project_name="Demo Losa 4.5m — Cochabamba")
