import dataclasses as _dc
import typing as _tp

from .. import common as _common


@_dc.dataclass
class CollectorField:
    area_m2: _common.ScaledValue["PerDemandValueType"]
    inclination_deg: float
    orientation_east_west_deg: float
    type: "CollectorScaling"
    performance_coefficients: "PerformanceCoefficients"
    nominal_mass_kg_per_h: _common.ScaledValue["PerCollectorAreaScaling"]


type PerDemandValueType = _tp.Literal[
    "absolute_1", "relative_to_demand_per_GWh"
]

type CollectorScaling = _tp.Literal["flat-plate", "parallel-trough"]

type PerCollectorAreaScaling = _tp.Literal[
    "absolute_1", "relative_to_collector_area_per_m2"
]


@_dc.dataclass
class PerformanceCoefficients:
    a0: float
    a1_kW_per_m2_per_K: float
    a2_kW_per_m2_per_K2: float
