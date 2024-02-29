import functools
from enum import Enum
from typing import List

from .BaseCommand import BaseCommand


class VariousModeSettings(BaseCommand):
    class Settings(Enum):
        AUTO_CUT = 0x40
        MIRROR_PRINTING = 0x80

    def __init__(self, settings: List[Settings] | None = None):
        super().__init__()
        self.settings = settings or []

    def to_bytes(self) -> bytes:
        return b'\x1BiM' + functools.reduce(lambda a, b: a | b, self.settings, 0x00).to_bytes()
