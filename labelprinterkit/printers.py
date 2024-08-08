from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from logging import getLogger
import struct
from typing import TypeVar

import packbits

from .backends import BaseBackend, UniDirectionalBackend
from .constants import Resolution, ErrorCodes, MediaType, StatusCodes, NotificationCodes, TapeColor, \
    TextColor, VariousModesSettings, AdvancedModeSettings, Media
from .job import Job

logger = getLogger(__name__)

BackendType = TypeVar('BackendType', bound=BaseBackend)


class Error:
    def __init__(self, byte1: int, byte2: int) -> None:
        value = byte1 | (byte2 << 8)
        self._errors = {
            err.name: bool(value & err_code)
            for err_code, err in {x.value: x for x in ErrorCodes}.items()
        }

    def any(self):
        return any(self._errors.values())

    def __getattr__(self, attr):
        return self._errors[attr]

    def __repr__(self):
        return "<Errors {}>".format(self._errors)


class Status:
    def __init__(self, data: bytes) -> None:
        _data = dict()
        # assert data[0] == 0x80  # Print head mark
        # assert data[1] == 0x20  # Size
        # assert data[2] == 0x42  # Brother code
        # assert data[3] == 0x30  # Series code
        _data['model'] = data[4]  # Model code
        # assert data[4] == 0x30  # Country code
        # assert data[5] == 0x00  # Reserved
        # assert data[6] == 0x00  # Reserved
        _data['errors'] = Error(data[8], data[9])
        _data['media_width'] = int(data[10])
        try:
            _data['media_type'] = {x.value: x for x in MediaType}[int(data[11])]
        except IndexError:
            raise RuntimeError("Unsupported media type {data[11]}")
        # assert data[12] == 0x00  # Number of colors
        # assert data[13] == 0x00  # Fonts
        # assert data[14] == 0x00  # Japanese Fonts
        # assert data[15] == 0x00  # Mode
        # assert data[16] == 0x00  # Density
        # assert data[17] == 0x00  # Media length
        try:
            _data['status'] = {x.value: x for x in StatusCodes}[int(data[18])]
        except IndexError:
            raise RuntimeError("Unknown status {data[18]}")
        # assert data[19] == 0x00  # Phase type
        # assert data[20] == 0x00  # Phase number (higher order bytes)
        # assert data[21] == 0x00  # Phase number (lower order bytes)
        try:
            _data['notification'] = {x.value: x for x in NotificationCodes}[int(data[22])]
        except IndexError:
            raise RuntimeError("Unknown notification {data[18]}")
        # assert data[23] == 0x00  # Expansion area
        try:
            _data['tape_color'] = {x.value: x for x in TapeColor}[int(data[24])]
        except IndexError:
            raise RuntimeError("Unknown tape color {data[18]}")
        try:
            _data['text_color'] = {x.value: x for x in TextColor}[int(data[25])]
        except IndexError:
            raise RuntimeError("Unknown text color {data[18]}")
        # data[26:29]  # Hardware settings
        # data[30:31] Reserved

        self._data = _data
        self._media = None

    def __repr__(self) -> str:
        return "<Status {}>".format(self._data)

    def __getattr__(self, attr):
        return self._data[attr]

    def ready(self) -> bool:
        return not self.errors.any()

    @property
    def media(self) -> Media:
        if self._media is None:
            self._media = Media.get_media(self.media_width, self.media_type)
        return self._media

    @property
    def status(self) -> Media:
        if self._data['status'] is not None:
            return self._data['status']


class BasePrinter(ABC):
    """Base class for printers. All printers define this API.  Any other
    methods are prefixed with a _ to indicate they are not part of the
    printer API"""

    def __init__(self, backend: BackendType):
        self._backend = backend

    @abstractmethod
    def print(self, job: Job):
        ...


def encode_line(bitmap_line: bytes, padding) -> bytes:
    # The number of bits we need to add left or right is not always a multiple
    # of 8, so we need to convert our line into an int, shift it over by the
    # left margin and convert it to back again, padding to 16 bytes.

    # print("".join(f"{x:08b}".replace("0", " ") for x in bytes(bitmap_line)))
    line_int = int.from_bytes(bitmap_line, byteorder='big')
    line_int <<= padding
    padded = line_int.to_bytes(16, byteorder='big')

    # pad to 16 bytes
    compressed = packbits.encode(padded)
    logger.debug("original bitmap: %s", bitmap_line)
    logger.debug("padded bitmap %s", padded)
    logger.debug("packbit compressed %s", compressed)
    # <h: big endian short (2 bytes)
    prefix = struct.pack("<H", len(compressed))

    return prefix + compressed


class GenericPrinter(BasePrinter):
    _SUPPORTED_RESOLUTIONS = (Resolution.LOW, Resolution.HIGH)
    _FEATURE_HALF_CUT = True

    def __init__(self, backend: BackendType):
        super().__init__(backend)

    def reset(self):
        self._backend.write(b'\x00' * 100)  # Invalidate command
        self._backend.write(b'\x1b@')  # Initialize command 1b 40

    def get_status(self) -> Status:
        if hasattr(self._backend, 'get_status'):
            data = self._backend.get_status()
        elif isinstance(self._backend, UniDirectionalBackend):
            raise RuntimeError("Backend is unidirectional")
        else:
            self.reset()
            self._backend.write(b'\x1BiS')
            data = self._backend.read(32)
        if not data:
            raise IOError("No Response from printer")

        if len(data) < 32:
            raise IOError("Invalid Response from printer")

        return Status(data)

    def print(self, job: Job):
        logger.info("starting print")

        self.reset()

        if job.media in (Media.NO_MEDIA, Media.UNSUPPORTED_MEDIA):
            raise RuntimeError('Unsupported Media')

        if job.resolution not in self._SUPPORTED_RESOLUTIONS:
            raise RuntimeError('Resolution is not supported by this printer.')

        media_type = job.media.value.media_type.value.to_bytes(1, 'big')
        media_size = job.media.value.width.to_bytes(1, 'big')
        offset = job.media.value.lmargin

        various_mode = 0
        if job.auto_cut:
            various_mode = various_mode | VariousModesSettings.AUTO_CUT.value
            auto_cut = True
        else:
            auto_cut = False
        if job.mirror_printing:
            various_mode = various_mode | VariousModesSettings.MIRROR_PRINTING.value
        various_mode = various_mode.to_bytes(1, 'big')

        advanced_mode = 0
        if job.half_cut:
            if not self._FEATURE_HALF_CUT:
                raise RuntimeError('Half cut is not supported by this printer.')
            advanced_mode = advanced_mode | AdvancedModeSettings.HALF_CUT.value
        if not job.chain:
            advanced_mode = advanced_mode | AdvancedModeSettings.CHAIN_PRINTING.value
        if job.special_tape:
            advanced_mode = advanced_mode | AdvancedModeSettings.SPECIAL_TAPE.value
        if job.resolution == Resolution.HIGH:
            margin = b'\x1C\x00'
            advanced_mode = advanced_mode | AdvancedModeSettings.HIGH_RESOLUTION.value
        else:
            margin = b'\x0E\x00'
        advanced_mode = advanced_mode.to_bytes(1, 'big')

        cut_each = job.cut_each.to_bytes(1, 'big')

        for i, page in enumerate(job):
            # switch dynamic command mode: enable raster mode
            self._backend.write(b'\x1Bia\x01')

            # Print information command
            # b'\x1Biz\x86\x01\x0c\x00\x00\x00\00\x00\x00'
            information_command = b'\x1Biz\x86' + media_type + media_size + b'\x00\x00\x00\00\x00\x00'
            self._backend.write(information_command)
            if i == 0 and auto_cut:
                # Ugly workaround
                # Print information command a second time forces cutting after first page.
                # No idea why this is needed, but it works
                self._backend.write(information_command)

            # Various mode
            logger.debug(f"various_mode: {various_mode}")
            self._backend.write(b'\x1BiM' + various_mode)

            # Advanced mode
            logger.debug(f"advanced_mode: {advanced_mode}")
            self._backend.write(b'\x1biK' + advanced_mode)

            # margin
            self._backend.write(b'\x1bid' + margin)

            if auto_cut:
                # Configure after how many pages a cut should be done
                self._backend.write(b'\x1BiA' + cut_each)

            # Enable compression mode
            self._backend.write(b'M\x02')

            # send rastered lines
            for line in page:
                logging.debug(f"line: {line}")
                self._backend.write(b'G' + encode_line(line, offset))

            self._backend.write(b'Z')

            logging.debug(f"i: {i}")
            if i < len(job) - 1:
                self._backend.write(b'\x0C')

                while not self.__is_print_finished(page.length*1000):
                    pass

        # end page
        self._backend.write(b'\x1A')
        logger.info("end of page")

    def __is_print_finished(self, timeout):
        data = self._backend.read(32, timeout)
        while data is None:
            data = self._backend.read(32, timeout)

        return Status(data).status == StatusCodes.PRINTING_DONE


class P700(GenericPrinter):
    pass


class P750W(GenericPrinter):
    pass


class P2730(GenericPrinter):
    pass


class H500(GenericPrinter):
    _SUPPORTED_RESOLUTIONS = (Resolution.LOW,)
    _FEATURE_HALF_CUT = False


class E500(H500):
    pass


class E550W(P750W):
    pass
