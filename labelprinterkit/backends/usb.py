from __future__ import annotations

from time import sleep

import usb.core
import usb.util

from . import BaseBackend


class PyUSBBackend(BaseBackend):
    """Assumes only a SINGLE USB Printer / Brother Device is Attached"""

    def __init__(self) -> None:
        self._dev = PyUSBBackend.get_device()

    @staticmethod
    def get_device() -> usb.core.Device:
        """Get the PyUSB Device for a USB Printer"""
        dev = usb.core.find(custom_match=PyUSBBackend.is_usb_printer)
        if dev is None:
            raise OSError("No Printer Found")
        return dev

    @staticmethod
    def is_usb_printer(dev) -> bool:
        """Check if the Device is a USB Printer - by Device Class or Interface Class"""
        if dev.bDeviceClass == 7:
            return True
        for cfg in dev:
            if usb.util.find_descriptor(cfg, bInterfaceClass=7) is not None:
                return True
        return False

    @staticmethod
    def is_brother_manufacturer(dev) -> bool:
        """Check if the Device is a Brother Printer - by Manufacturer"""
        try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer)
        except (usb.core.USBError, ValueError):
            manufacturer = None

        if manufacturer == "Brother":
            return True
        return False

    def detach_from_kernel(self) -> None:
        """
        Detach the given Device from the Kernel - allowing PyUSB Exclusive Access
        Required for: usb.core.USBError: [Errno 16] Resource busy
        """
        self._dev.reset()

        interface = self._dev[0].interfaces()[0].bInterfaceNumber
        if self._dev.is_kernel_driver_active(interface):
            try:
                self._dev.detach_kernel_driver(interface)
            except usb.core.USBError:
                pass

        self._dev.set_configuration()

        self.refresh()

    def refresh(self) -> None:
        self._dev = PyUSBBackend.get_device()

    def write(self, data: bytes) -> None:
        self._dev.write(0x2, data)

    def read(self, count: int) -> bytes | None:
        for _ in range(0, 3):
            data = self._dev.read(0x81, count)
            if data:
                return data
            sleep(0.1)
        return None
