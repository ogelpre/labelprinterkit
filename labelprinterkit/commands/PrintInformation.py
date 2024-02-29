from enum import Enum

from .BaseCommand import BaseCommand
from ..constants import MediaType


class PrintInformation(BaseCommand):
    class Page(Enum):
        STARTING_PAGE = 0
        OTHER_PAGE = 1
        LAST_PAGE = 2

    def __init__(self,
                 media_type: MediaType | None,
                 high_resolution: bool | None,
                 media_width: int | None,
                 raster_number: int | None = 0,
                 page: Page = Page.STARTING_PAGE,
                 recovery: bool = False,
                 ):
        super().__init__()
        self.media_type = media_type
        self.high_resolution = high_resolution
        self.media_width = media_width
        self.raster_number = raster_number
        self.page = page
        self.recovery = recovery

    def to_bytes(self) -> bytes:
        valid = 0x00
        if self.media_type is not None:
            valid = valid | 0x02
        if self.media_width is not None:
            valid = valid | 0x04
        if self.recovery:
            valid = valid | 0x80

        media_type = 0x00
        if media_type == MediaType.LAMINATED_TAPE and self.high_resolution:
            media_type = 0x09
        elif media_type == MediaType.HEATSHRINK_TUBE_21:
            media_type = 0x11
        elif media_type == MediaType.HEATSHRINK_TUBE_31:
            media_type = 0x17
        elif media_type == MediaType.FLE_TAPE:
            media_type = 0x13

        return b'\x1Biz' + \
               valid.to_bytes() + \
               media_type.to_bytes() + \
               self.media_width.to_bytes() if self.media_width is not None else b'\x00' + \
                                                                                b'\x00' + \
                                                                                (
                                                                                    self.raster_number if self.raster_number is not None else 0).to_bytes(
                                                                                    3, 'big') + \
                                                                                self.page.value.to_bytes() + \
                                                                                b'\x00'
