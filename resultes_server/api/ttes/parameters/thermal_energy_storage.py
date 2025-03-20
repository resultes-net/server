import typing as _tp

import pydantic as _pc


class TtesStorage(_pc.BaseModel):
    size: _tp.Union[
        "TtesSizeScaledHeight", "TtesSizeScaledFloorArea", "TtesSizeAbsolute"
    ] = _pc.Field(discriminator="size_type")
    location: "TtesLocation"
    heat_conductance_kW_per_m2_per_K: float
    ports_relative_heights_1: "TtesPortRelativeHeights" = _pc.Field(
        description="The heights are relative: 1 means at the very top, 0.5 in the middle, etc."
    )


class TtesSizeScaledHeight(_pc.BaseModel):
    size_type: _tp.Literal["scaled_height"]
    height_relative_to_demand_m_per_GWh: float
    floor_area_m2: float


class TtesSizeScaledFloorArea(_pc.BaseModel):
    size_type: _tp.Literal["scaled-floor-area"]
    height_m: float
    floor_area_relative_to_demand_m2_per_GWh: float


class TtesSizeAbsolute(_pc.BaseModel):
    size_type: _tp.Literal["absolute"]
    volume_m3: float


TtesLocation = _tp.Literal["above-ground-free-standing", "below-ground-buried"]


class TtesPortRelativeHeights(_pc.BaseModel):
    """The heights ar relative: 1 is at the very top, 0.5 in the middle, etc."""

    top: float
    middle: float
    bottom: float

    @_pc.model_validator(mode="after")
    def _validate_port_heights_order(self) -> _tp.Self:
        if not (self.top > self.middle > self.bottom):
            raise ValueError("Port heights must decrease from top to bottom.")

        return self
