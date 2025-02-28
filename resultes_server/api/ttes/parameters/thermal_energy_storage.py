import dataclasses as _dc
import typing as _tp

import resultes_server.api.common as _acom


@_dc.dataclass
class TtesStorage:
    size: _tp.Union[
        "TtesSizeScaledHeight", "TtesSizeScaledFloorArea", "TtesSizeAbsolute"
    ] = _acom.field(discriminator="size_type")
    location: "TtesLocation"
    heat_conductance_kW_per_m2_per_K: float
    ports_relative_heights_1: "TtesPortRelativeHeights" = _acom.field(
        "The heights are relative: 1 means at the very top, 0.5 in the middle, etc."
    )


@_dc.dataclass
class TtesSizeScaledHeight:
    size_type: _tp.Literal["scaled_height"]
    height_relative_to_demand_m_per_GWh: float
    floor_area_m2: float


@_dc.dataclass
class TtesSizeScaledFloorArea:
    size_type: _tp.Literal["scaled-floor-area"]
    height_m: float
    floor_area_relative_to_demand_m2_per_GWh: float


@_dc.dataclass
class TtesSizeAbsolute:
    size_type: _tp.Literal["absolute"]
    volume_m3: float


TtesLocation = _tp.Literal["above-ground-free-standing", "below-ground-buried"]


@_dc.dataclass
class TtesPortRelativeHeights:
    """The heights ar relative: 1 is at the very top, 0.5 in the middle, etc."""

    top: float
    middle: float
    bottom: float
    
    def __post_init__(self) -> None:
        if not (self.top > self.middle > self.bottom):
            raise ValueError("Port heights must decrease from top to bottom.")
