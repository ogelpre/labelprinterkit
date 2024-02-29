import struct

import packbits

from .logger import logger
from ..constants import PrintHeadMediaAlignment, PrintHeadHeight


def encode_line(bitmap_line: bytes, phma: PrintHeadMediaAlignment, phh: PrintHeadHeight) -> bytes:
    if phma.left_margin + phma.print_area + phma.right_margin != phh.value:
        raise ValueError("Print head media alignment does not match print head height")

    # The number of bits we need to add left or right is not always a multiple
    # of 8, so we need to convert our line into an int, shift it over by the
    # left margin and convert it to back again, padding to 16 bytes.

    line_int = int.from_bytes(bitmap_line, byteorder='big')
    line_int <<= phma.left_margin
    padded = line_int.to_bytes(phh.value // 8, byteorder='big')

    # pad to 16 bytes
    compressed = packbits.encode(padded)
    logger.debug("original bitmap: %s", bitmap_line)
    logger.debug("padded bitmap %s", padded)
    logger.debug("packbit compressed %s", compressed)
    # <h: big endian short (2 bytes)
    prefix = struct.pack("<H", len(compressed))

    return prefix + compressed
