from .GenericPrinter import GenericPrinter
from ..constants import Resolution


class H500(GenericPrinter):
    _SUPPORTED_RESOLUTIONS = (Resolution.LOW,)
    _FEATURE_HALF_CUT = False
