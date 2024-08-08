from __future__ import annotations

try:
    import serial
except ImportError:
    serial = None
from . import BiDirectionalBackend


class BTSerialBackend(BiDirectionalBackend):
    def __init__(self, dev_path: str):
        if serial is None:
            raise RuntimeError('Bluetooth is not supported. Pacakge serial is missing.')
        dev = serial.Serial(
            dev_path,
            baudrate=9600,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            bytesize=8,
            dsrdtr=False,
            timeout=1
        )
        if dev is None:
            raise OSError('Device not found')
        self._dev = dev

    def write(self, data: bytes):
        self._dev.write(data)

    def read(self, count: int, timeout=None) -> bytes:
        data = self._dev.read(count)
        return data
