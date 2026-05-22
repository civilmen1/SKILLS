"""Modelos de datos (dataclasses) para entradas y resultados."""
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class Materials:
    """Parámetros de materiales según NB 1225001."""
    fc: float          # Resistencia característica hormigón [MPa]
    fy: float          # Límite de fluencia del acero [MPa]
    cover: float = 0.025   # Recubrimiento nominal [m]

    @property
    def Ec(self) -> float:
        """Módulo de elasticidad del hormigón [MPa], NB 1225001."""
        return 4700 * (self.fc ** 0.5)

    @property
    def Es(self) -> float:
        """Módulo de elasticidad del acero [MPa]."""
        return 200_000.0


@dataclass
class Loads:
    """Cargas de diseño [kN/m2]."""
    dead: float          # Carga muerta adicional (acabados, etc.)
    live: float          # Carga viva
    dead_sw: float = 0.0  # Peso propio calculado automáticamente si 0


@dataclass
class SeismicParams:
    """Parámetros sísmicos según NBDS-2023."""
    So: float                      # Aceleración pico del sitio [g]
    soil_type: Literal["S1", "S2", "S3", "S4"] = "S2"
    category: Literal["A", "B", "C", "D"] = "C"
    importance_factor: float = 1.0  # Factor de importancia I
    R: float = 4.0                  # Factor de reducción de respuesta


@dataclass
class SlabConstraints:
    """Restricciones constructivas para losas."""
    h_min: float = 0.10              # Espesor mínimo [m]
    h_max: float = 0.30              # Espesor máximo [m]
    h_step: float = 0.01             # Paso de búsqueda de espesor [m]
    bar_diameters: list[int] = field(default_factory=lambda: [8, 10, 12])  # [mm]
    spacing_options: list[float] = field(
        default_factory=lambda: [0.10, 0.125, 0.15, 0.175, 0.20, 0.25]
    )  # [m]
    deflection_limit: float = 250.0  # L / deflection_limit


@dataclass
class SlabResult:
    """Resultado de la optimización de losa."""
    h: float                  # Espesor óptimo [m]
    As_main: float            # Armadura principal requerida [cm2/m]
    As_dist: float            # Armadura de distribución [cm2/m]
    bar_main: int             # Diámetro barra principal [mm]
    bar_dist: int             # Diámetro barra distribución [mm]
    spacing_main: float       # Separación armadura principal [m]
    spacing_dist: float       # Separación armadura distribución [m]
    Mu_design: float          # Momento de diseño [kN·m/m]
    MRd: float                # Momento resistente [kN·m/m]
    checks: dict              # Verificaciones normativas {nombre: pass/fail}
    alternatives: list        # Soluciones alternativas cercanas
    cost_index: float         # Índice de costo relativo (acero + hormigón)
