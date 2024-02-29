from .BaseCommand import BaseCommand


class Initialize(BaseCommand):
    def to_bytes(self) -> bytes:
        return b'\x1b@'
