from . import user as _user
from .simulations import simulation as _sim

_sim.Simulation.model_rebuild()
_user.User.model_rebuild()
