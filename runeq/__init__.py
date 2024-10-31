"""
The Rune Labs Standard Development Kit (SDK) for querying data from Rune
APIs.

"""

from . import resources
from .config import Config
from .resources.client import initialize

__all__ = [
    "Config",
    "initialize",
    "resources",
]
