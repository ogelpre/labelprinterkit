from .BaseCommand import BaseCommand


class ZeroRasterGraphics(BaseCommand):
    def to_bytes(self) -> bytes:
        return b'Z'
