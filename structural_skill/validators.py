"""Validaciones de entrada para los parámetros del skill."""
from structural_skill.models import Materials, Loads, SeismicParams, SlabConstraints


def validate_materials(m: Materials) -> list[str]:
    """Retorna lista de errores de validación para materiales."""
    errors = []
    if not (14 <= m.fc <= 70):
        errors.append(f"fc={m.fc} MPa fuera de rango admisible [14–70 MPa] (NB 1225001)")
    if m.fy not in (280, 350, 420, 500, 550):
        # Advertencia, no error crítico
        errors.append(f"fy={m.fy} MPa: verificar que el acero sea grado comercial disponible en Bolivia")
    if not (0.010 <= m.cover <= 0.075):
        errors.append(f"Recubrimiento={m.cover*100:.0f}cm fuera de rango típico [1–7.5 cm]")
    return errors


def validate_loads(l: Loads) -> list[str]:
    errors = []
    if l.dead < 0:
        errors.append("Carga muerta no puede ser negativa")
    if l.live <= 0:
        errors.append("Carga viva debe ser mayor a 0")
    return errors


def validate_seismic(s: SeismicParams) -> list[str]:
    errors = []
    if not (0.05 <= s.So <= 0.80):
        errors.append(f"So={s.So}g fuera del rango típico boliviano [0.05–0.80g] (NBDS-2023)")
    if s.R <= 0:
        errors.append("Factor R debe ser positivo")
    if s.importance_factor not in (1.0, 1.25, 1.5):
        errors.append(f"Factor de importancia I={s.importance_factor}: verifique según categoría NBDS-2023")
    return errors


def validate_slab_constraints(c: SlabConstraints) -> list[str]:
    errors = []
    if c.h_min < 0.05:
        errors.append("Espesor mínimo de losa < 5cm no es constructivo")
    if c.h_max > 0.50:
        errors.append("Espesor máximo de losa > 50cm: verifique si no es mejor otro sistema")
    if not c.bar_diameters:
        errors.append("Debe especificar al menos un diámetro de barra")
    if not c.spacing_options:
        errors.append("Debe especificar al menos una opción de separación")
    return errors
