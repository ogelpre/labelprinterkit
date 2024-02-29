from .BaseCommand import BaseCommand


class RasterGraphicsTransfer(BaseCommand):
    def __init__(self, data: bytes):
        super().__init__()
        self.data = data

    def to_bytes(self) -> bytes:
        return b'G' + len(self.data).to_bytes(2, 'big') + self.data
