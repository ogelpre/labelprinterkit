from .GenericPrinter import GenericPrinter
from ..constants import PrintHeadHeight


class P900(GenericPrinter):
    _PRINT_HEAD_HEIGHT = PrintHeadHeight.PHH560
