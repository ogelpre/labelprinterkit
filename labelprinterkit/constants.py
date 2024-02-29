from __future__ import annotations

from enum import Enum
from typing import NamedTuple, Tuple


class Resolution(Enum):
    LOW = (180, 180)
    HIGH = (180, 320)


class ErrorCodes(Enum):
    NO_MEDIA = 0x0001
    CUTTER_JAM = 0x0004
    WEAK_BATTERY = 0x0008
    HIGH_VOLTAGE_ADAPTER = 0x0040
    REPLACE_MEDIA = 0x0100
    COVER_OPEN = 0x1000
    OVERHEATING = 0x2000


class PrintHeadHeight(Enum):
    PHH128 = 128
    PHH560 = 560


class MediaType(Enum):
    NO_MEDIA = 0x00
    LAMINATED_TAPE = 0x01
    NON_LAMINATED_TAPE = 0x03
    HEATSHRINK_TUBE_21 = 0x11
    HEATSHRINK_TUBE_31 = 0x17
    INCOMPATIBLE_TAPE = 0xFF

    # PT-P900/P900W/P950NW/P910BT
    FABRIC_TAPE = 0x04
    FLE_TAPE = 0x13
    FLEXIBLE_ID_TAPE = 0x14
    SATIN_TAPE = 0x15


class TapeInfo(NamedTuple):
    media_type: MediaType | None
    width: float
    length: float | None  # None for continuous tape
    media_width: int
    media_length: int = 0x00


class Media(Enum):
    UNSUPPORTED_MEDIA = TapeInfo(None, 0, None, 0x00)
    NO_MEDIA = TapeInfo(None, 0, None, 0x00)
    TZE_3_5 = TapeInfo(MediaType.LAMINATED_TAPE, 3.5, None, 0x04)
    TZE_6 = TapeInfo(MediaType.LAMINATED_TAPE, 6, None, 0x06)
    TZE_9 = TapeInfo(MediaType.LAMINATED_TAPE, 9, None, 0x09)
    TZE_12 = TapeInfo(MediaType.LAMINATED_TAPE, 12, None, 0x0C)
    TZE_18 = TapeInfo(MediaType.LAMINATED_TAPE, 18, None, 0x12)
    TZE_24 = TapeInfo(MediaType.LAMINATED_TAPE, 24, None, 0x18)
    TZE_36 = TapeInfo(MediaType.LAMINATED_TAPE, 36, None, 0x24)
    HS_5_8 = TapeInfo(MediaType.HEATSHRINK_TUBE_21, 5.8, None, 0x06)
    HS_8_8 = TapeInfo(MediaType.HEATSHRINK_TUBE_21, 8.8, None, 0x09)
    HS_11_7 = TapeInfo(MediaType.HEATSHRINK_TUBE_21, 11.7, None, 0x0C)
    HS_17_7 = TapeInfo(MediaType.HEATSHRINK_TUBE_21, 17.7, None, 0x12)
    HS_23_6 = TapeInfo(MediaType.HEATSHRINK_TUBE_21, 23.6, None, 0x18)
    FLE_21_45 = TapeInfo(MediaType.FLE_TAPE, 21, None, 0x15, 0x2D)

    @classmethod
    def get_media(cls, width: float, media_type: MediaType):
        medias = [media_size for media_size in cls
                  if media_size.value.width == width and media_size.value.media_type == media_type]
        if not medias:
            return cls.UNSUPPORTED_MEDIA
        return medias[0]


class PrintHeadMediaAlignment(NamedTuple):
    left_margin: int
    print_area: int
    right_margin: int


PRINTHEAD_MEDIA_ALIGNMENT: dict[Tuple[PrintHeadHeight, Media], PrintHeadMediaAlignment] = {
    # (PrintHeadHeight.PHW128, Media.TZE_*)
    (PrintHeadHeight.PHH128, Media.TZE_3_5): PrintHeadMediaAlignment(52, 24, 52),
    (PrintHeadHeight.PHH128, Media.TZE_6): PrintHeadMediaAlignment(48, 32, 48),
    (PrintHeadHeight.PHH128, Media.TZE_9): PrintHeadMediaAlignment(39, 50, 39),
    (PrintHeadHeight.PHH128, Media.TZE_12): PrintHeadMediaAlignment(29, 70, 29),
    (PrintHeadHeight.PHH128, Media.TZE_18): PrintHeadMediaAlignment(8, 112, 8),
    (PrintHeadHeight.PHH128, Media.TZE_24): PrintHeadMediaAlignment(0, 128, 0),

    # (PrintHeadHeight.PHW128, Media.HS_*)
    (PrintHeadHeight.PHH128, Media.HS_5_8): PrintHeadMediaAlignment(50, 28, 50),
    (PrintHeadHeight.PHH128, Media.HS_8_8): PrintHeadMediaAlignment(40, 48, 40),
    (PrintHeadHeight.PHH128, Media.HS_11_7): PrintHeadMediaAlignment(31, 66, 31),
    (PrintHeadHeight.PHH128, Media.HS_17_7): PrintHeadMediaAlignment(11, 106, 11),
    (PrintHeadHeight.PHH128, Media.HS_23_6): PrintHeadMediaAlignment(0, 128, 0),
    # PT-E550W/P750W/P710BT additionally support HS 5.2, 9, 11.2, 21 but codes are unknown

    # (PrintHeadHeight.PHW560, Media.TZE_*)
    (PrintHeadHeight.PHH560, Media.TZE_3_5): PrintHeadMediaAlignment(248, 48, 264),
    (PrintHeadHeight.PHH560, Media.TZE_6): PrintHeadMediaAlignment(240, 64, 256),
    (PrintHeadHeight.PHH560, Media.TZE_9): PrintHeadMediaAlignment(219, 106, 235),
    (PrintHeadHeight.PHH560, Media.TZE_12): PrintHeadMediaAlignment(197, 150, 213),
    (PrintHeadHeight.PHH560, Media.TZE_18): PrintHeadMediaAlignment(155, 234, 171),
    (PrintHeadHeight.PHH560, Media.TZE_24): PrintHeadMediaAlignment(112, 320, 128),
    (PrintHeadHeight.PHH560, Media.TZE_36): PrintHeadMediaAlignment(45, 454, 61),

    # (PrintHeadHeight.PHW560, Media.HS_*)
    (PrintHeadHeight.PHH560, Media.HS_5_8): PrintHeadMediaAlignment(244, 56, 260),
    (PrintHeadHeight.PHH560, Media.HS_8_8): PrintHeadMediaAlignment(224, 96, 240),
    (PrintHeadHeight.PHH560, Media.HS_11_7): PrintHeadMediaAlignment(206, 132, 222),
    (PrintHeadHeight.PHH560, Media.HS_17_7): PrintHeadMediaAlignment(166, 212, 182),
    (PrintHeadHeight.PHH560, Media.HS_23_6): PrintHeadMediaAlignment(144, 256, 160),
    # PT-P900/P900W/P950NW/P910BT additionally support HS 5.2, 9, 11.2, 21, 31 but codes are unknown
}

for (phh, media), phma in PRINTHEAD_MEDIA_ALIGNMENT.items():
    assert phma.left_margin + phma.print_area + phma.right_margin == phh.value


class StatusCodes(Enum):
    STATUS_REPLY = 0x00
    PRINTING_DONE = 0x01
    ERROR_OCCURRED = 0x02
    EDIT_IF_MODE = 0x03
    TURNED_OFF = 0x04
    NOTIFICATION = 0x05
    PHASE_CHANGE = 0x06


class NotificationCodes(Enum):
    NOT_AVAILABLE = 0x00
    COVER_OPEN = 0x01
    COVER_CLOSED = 0x02


class TapeColor(Enum):
    NO_MEDIA = 0x00
    WHITE = 0x01
    OTHER = 0x02
    CLEAR = 0x03
    RED = 0x04
    BLUE = 0x05
    YELLOW = 0x06
    GREEN = 0x07
    BLACK = 0x08
    CLEAR_WHITE_TEXT = 0x09
    MATTE_WHITE = 0x20
    MATTE_CLEAR = 0x21
    MATTE_SILVER = 0x22
    SATIN_GOLD = 0x23
    SATIN_SILVER = 0x24
    BLUE_D = 0x30
    RED_D = 0x31
    FLUORESCENT_ORANGE = 0x40
    FLUORESCENT_YELLOW = 0x41
    BERRY_PINK_S = 0x50
    LIGHT_GRAY_S = 0x51
    LIME_GREEN_S = 0x52
    YELLOW_F = 0x60
    PINK_F = 0x61
    BLUE_F = 0x62
    WHITE_HEAT_SHRINK_TUBE = 0x70
    WHITE_FLEX_ID = 0x90
    YELLOW_FLEX_ID = 0x91
    CLEANING = 0xF0
    STENCIL = 0xF1
    INCOMPATIBLE = 0xFF


class TextColor(Enum):
    NO_MEDIA = 0x00
    WHITE = 0x01
    OTHER = 0x02
    RED = 0x04
    BLUE = 0x05
    BLACK = 0x08
    GOLD = 0x0a
    BLUE_F = 0x62
    CLEANING = 0xF0
    STENCIL = 0xF1
    INCOMPATIBLE = 0xFF
