from .BaseCommand import BaseCommand


class SpecifyCutEachPages(BaseCommand):
    def __init__(self, pages: int):
        super().__init__()
        self.pages = pages

    def to_bytes(self) -> bytes:
        return b'\x1Bid' + self.pages.to_bytes()
