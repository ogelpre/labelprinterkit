from .BaseCommand import BaseCommand


class Invalidate(BaseCommand):
    def to_bytes(self) -> bytes:
        return b'\x00'
