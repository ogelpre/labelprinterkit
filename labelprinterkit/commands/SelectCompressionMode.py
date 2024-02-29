from enum import Enum

from .BaseCommand import BaseCommand


class SelectCompressionMode(BaseCommand):
    class Compression(Enum):
        NO_COMPRESSION = 0x00
        TIFF = 0x02

    def __init__(self, compression: Compression):
        super().__init__()
        self.compression = compression

    def to_bytes(self) -> bytes:
        return b'M' + self.compression.value.to_bytes()
