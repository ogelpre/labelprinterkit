from .BaseCommand import BaseCommand


class StatusInformationRequest(BaseCommand):
    def to_bytes(self) -> bytes:
        return b'\x1BiS'
