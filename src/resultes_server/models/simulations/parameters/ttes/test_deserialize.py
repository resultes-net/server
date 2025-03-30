import json as _json
import pprint as _pp

from typing import Literal

from . import *
from .parameters.thermal_energy_storage import *
from ..common import *
from ..common.collector_field import *
from ..common.demand import *

JSON = r"""
{
  "demand": {
    "profile": {
      "profile_type": "predefined",
      "name": "default"
    }
  },
  "collector_field": {
    "area": {
      "scaling": "relative_to_demand_m2_per_GWh",
      "value": 4
    },
    "inclination_deg": 45,
    "nominal_massflow": {
      "scaling": "relative_to_collector_area_kg_per_h_m2",
      "value": 15
    },
    "orientation_east_west_deg": 0,
    "performance_coefficients": {
      "a0": 0.857,
      "a1_kW_per_m2_per_K": 0.00416,
      "a2_kW_per_m2_per_K2": 0.0000089
    },
    "type": "flat-plate"
  },
  "storage": {
    "heat_conductance_kW_per_m2_per_K": 0.00008,
    "ports_relative_heights_1": {
      "top": 0.99,
      "middle": 0.5,
      "bottom": 0.01
    },
    "size": {
      "size_type": "scaled-floor-area",
      "floor_area_relative_to_demand_m2_per_GWh": 200,
      "height_m": 20
    },
    "location": "above-ground-free-standing"
  }
}
"""

EXPECTED_PARAMETERS = TtesParameters(
    demand=Demand(profile=PreDefinedProfile(profile_type="predefined", name="default")),
    collector_field=CollectorField(
        area=ScaledValue[Literal["absolute_m2", "relative_to_demand_m2_per_GWh"]](
            scaling="relative_to_demand_m2_per_GWh", value=4.0
        ),
        inclination_deg=45.0,
        orientation_east_west_deg=0.0,
        type="flat-plate",
        performance_coefficients=PerformanceCoefficients(
            a0=0.857, a1_kW_per_m2_per_K=0.00416, a2_kW_per_m2_per_K2=8.9e-06
        ),
        nominal_massflow=ScaledValue[
            Literal["absolute_kg_per_h", "relative_to_collector_area_kg_per_h_m2"]
        ](scaling="relative_to_collector_area_kg_per_h_m2", value=15.0),
    ),
    storage=TtesStorage(
        size=TtesSizeScaledFloorArea(
            size_type="scaled-floor-area",
            height_m=20.0,
            floor_area_relative_to_demand_m2_per_GWh=200.0,
        ),
        location="above-ground-free-standing",
        heat_conductance_kW_per_m2_per_K=8e-05,
        ports_relative_heights_1=TtesPortRelativeHeights(
            top=0.99, middle=0.5, bottom=0.01
        ),
    ),
)


def test_deserialize() -> None:
    data = _json.loads(JSON)

    actual_parameters = TtesParameters(**data)
    _pp.pprint(actual_parameters, indent=4)

    assert actual_parameters == EXPECTED_PARAMETERS
