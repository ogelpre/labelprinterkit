from .Error import Error
from ..constants import MediaType, StatusCodes, NotificationCodes, TapeColor, TextColor, Media


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
