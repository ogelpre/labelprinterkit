from .BaseCommand import BaseCommand


class Print(BaseCommand):
    def __init__(self, feed: bool = False):
        super().__init__()
        self.feed = feed

    def to_bytes(self) -> bytes:
        if self.feed:
            return b'\x1A'
        else:
            return b'\x0C'
