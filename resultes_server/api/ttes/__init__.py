import pydantic as _pc

from .parameters import thermal_energy_storage as _tes
from ..common import collector_field as _cf
from ..common import demand as _demand


class TtesParameters(_pc.BaseModel):
    demand: _demand.Demand
    collector_field: _cf.CollectorField
    storage: _tes.TtesStorage
