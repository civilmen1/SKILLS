# SKILLS — Optimización Estructural Bolivia

Módulo Python para optimización de secciones y armaduras de hormigón armado según:
- **NB 1225001** (versión 2019/2020) — Hormigón Estructural
- **NBDS-2023** — Norma Boliviana de Diseño Sísmico

## Alcance

| Elemento | Estado |
|---|---|
| Losas (unidireccional / bidireccional) | 🚧 En desarrollo |
| Vigas | ⏳ Próximo |
| Columnas | ⏳ Próximo |
| Fundaciones | ⏳ Próximo |

## Instalación

```bash
pip install -e .
```

## Uso rápido — Losa

```python
from structural_skill.slabs import optimize_slab

result = optimize_slab(
    slab_type="one_way",
    spans=[4.5],
    loads={"dead": 4.0, "live": 2.0},
    seismic={"So": 0.35, "soil_type": "S2", "category": "C"},
    materials={"fc": 21, "fy": 420},
    constraints={
        "h_min": 0.12, "h_max": 0.22,
        "bar_diameters": [8, 10, 12],
        "spacing": [0.10, 0.125, 0.15, 0.20]
    },
    objective="min_steel"
)
print(result)
```

## Estructura del proyecto

```
structural_skill/
├── nbds2023.py       # Cálculo sísmico NBDS-2023
├── nb1225001.py      # Verificaciones NB 1225001
├── models.py         # Clases de datos (dataclasses)
├── slabs.py          # Optimización de losas
├── beams.py          # Optimización de vigas (próximo)
├── columns.py        # Optimización de columnas (próximo)
├── foundations.py    # Optimización de fundaciones (próximo)
├── optimizer.py      # Motor de búsqueda discreta
├── validators.py     # Validaciones de entrada
└── reports.py        # Generación de reportes
```
