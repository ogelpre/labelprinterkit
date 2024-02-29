from __future__ import annotations

from pkg_resources import get_distribution,DistributionNotFound

__all__ = ["printers", "backends", "label", "job", "page"]
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
