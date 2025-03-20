import typing as _tp

import pydantic as _pc

from .. import common as _common


class CollectorField(_pc.BaseModel):
    area: _common.ScaledValue[
        _tp.Literal["absolute_m2", "relative_to_demand_m2_per_GWh"]
    ]
    inclination_deg: float
    orientation_east_west_deg: float
    type: "CollectorType"
    performance_coefficients: "PerformanceCoefficients"
    nominal_massflow: _common.ScaledValue[
        _tp.Literal[
            "absolute_kg_per_h", "relative_to_collector_area_kg_per_h_m2"
        ]
    ]


type CollectorType = _tp.Literal["flat-plate", "parallel-trough"]


class PerformanceCoefficients(_pc.BaseModel):
    a0: float
    a1_kW_per_m2_per_K: float
    a2_kW_per_m2_per_K2: float
