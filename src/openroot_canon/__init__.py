"""OpenRoot foundation library. Import this. Cite N-ids. Do not rewrite the locks."""
from .laws import coord, eta, gamma, landauer, synergy
from .newton import derive, load_canon, newton, postulate

__all__ = [
    "coord",
    "eta",
    "gamma",
    "landauer",
    "synergy",
    "newton",
    "derive",
    "postulate",
    "load_canon",
]
__version__ = "1.0.0"
