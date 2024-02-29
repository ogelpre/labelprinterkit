from __future__ import annotations

from time import sleep
from typing import Type

import usb.core
import usb.util

from . import BaseBackend, Command


class PyUSBBackend(BaseBackend):
    def __init__(self):
        dev = usb.core.find(custom_match=self.is_usb_printer)
        if dev is None:
            raise OSError('Device not found')
        self._dev = dev

    @staticmethod
    def is_usb_printer(dev) -> bool:
        if dev.bDeviceClass == 7:
            return True
        for cfg in dev:
            if usb.util.find_descriptor(cfg, bInterfaceClass=7) is not None:
                return True
        return False

    def write(self, data: bytes | Type[Command]):
        if isinstance(data, Command):
            data = data.to_bytes()
        self._dev.write(0x2, data)

    def read(self, count: int) -> bytes | None:
        for i in range(0, 3):
            data = self._dev.read(0x81, count)
            if data:
                return data
            sleep(0.1)
        return None
