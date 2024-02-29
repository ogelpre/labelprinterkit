import functools
from enum import Enum
from typing import List

from .BaseCommand import BaseCommand


class AdvancedModeSettings(BaseCommand):
    class Settings(Enum):
        DRAFT_PRINTING = 0b00000001
        HALF_CUT = 0b00000100
        NO_CHAIN_PRINTING = 0b00001000
        SPECIAL_TAPE = 0b00010000
        HIGH_RESOLUTION = 0b01000000
        NO_BUFFER_CLEARING = 0b10000000

    def __init__(self, settings: List[Settings] | None = None):
        super().__init__()
        self.settings = settings or []

    def to_bytes(self) -> bytes:
        return b'\x1BiM' + functools.reduce(lambda a, b: a | b.value, self.settings, 0x00).to_bytes()
