from enum import Enum

from .BaseCommand import BaseCommand


class SwitchDynamicCommandMode(BaseCommand):
    class Modes(Enum):
        ESC_P = 0x00
        RASTER = 0x01
        P_TOUCH_TEMPLATE = 0x02

    def __init__(self, mode: Modes = Modes.RASTER):
        super().__init__()
        self.mode = mode

    def to_bytes(self) -> bytes:
        return b'\x1Bia' + self.mode.value.to_bytes()
