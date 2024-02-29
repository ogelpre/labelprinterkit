from .BaseCommand import BaseCommand


class SpecifyMarginAmount(BaseCommand):
    def __init__(self, margin: int):
        super().__init__()
        self.margin = margin

    def to_bytes(self) -> bytes:
        return b'\x1Bid' + self.margin.to_bytes(2, 'little')
