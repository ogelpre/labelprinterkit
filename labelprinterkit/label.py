from __future__ import annotations

from abc import ABC, abstractmethod
from logging import getLogger
from math import ceil
from typing import TypeVar, NamedTuple, Optional

from PIL import Image, ImageChops, ImageDraw, ImageFont

try:
    from qrcode import QRCode as _QRCode
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_H, ERROR_CORRECT_Q
except ImportError:
    _QRCode = None
    ERROR_CORRECT_L = 1
    ERROR_CORRECT_M = 0
    ERROR_CORRECT_Q = 3
    ERROR_CORRECT_H = 2

from .constants import Resolution
from .page import BasePage, image_to_bitmap, bitmap_to_image

logger = getLogger(__name__)


def crop(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
        return im


class Padding(NamedTuple):
    left: int
    top: int
    bottom: int
    right: int


class Item(ABC):
    @abstractmethod
    def render(self) -> Image:
        ...


ItemType = TypeVar('ItemType', bound=Item)


class Text(Item):
    def __init__(self, height: int, text: str, font_path: str, font_index: int = 0, font_size: int | None = None,
                 padding: Padding = Padding(0, 0, 0, 0)):
        self.text = text
        self.height = height
        self.font_path = font_path
        self.font_index = font_index
        self.font_size = font_size

        if any([i < 0 for i in padding]):
            raise ValueError("Negative padding is not supported: {padding}")
        self.padding = padding

    def render(self) -> Image:
        iheight = self.height - self.padding.top - self.padding.bottom
        if self.font_size is None:
            font_size = self._calc_font_size(iheight)
            logger.debug(f"text: {self.text}, calculated font size: {font_size}")
        else:
            font_size = self.font_size
        font = ImageFont.truetype(self.font_path, font_size, self.font_index)
        text_x, _ = font.getsize(self.text)
        image = Image.new("1", (self.padding.left + text_x + self.padding.right, self.height), "white")
        fimage = Image.new("1", font.getsize(self.text), "white")
        draw = ImageDraw.Draw(fimage)
        draw.text((0, 0), self.text, "black", font)
        fimage = crop(fimage)
        image.paste(fimage, (self.padding.left, self.padding.top))
        return image

    def _calc_font_size(self, height: int) -> int:
        lower = 1
        upper = 1
        while True:
            font = ImageFont.truetype(self.font_path, upper)
            image = Image.new("1", font.getsize(self.text), "white")
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), self.text, "black", font)
            font_height = crop(image).size[1]
            if font_height >= height:
                break
            lower = upper
            upper *= 2
        while True:
            test = ceil((upper + lower) / 2)
            font = ImageFont.truetype(self.font_path, test)
            image = Image.new("1", font.getsize(self.text), "white")
            draw = ImageDraw.Draw(image)
            draw.text((0, 0), self.text, "black", font)
            font_height = crop(image).size[1]
            if upper - lower <= 1:
                return lower
            elif font_height > height:
                upper = test
            elif font_height < height:
                lower = test
            else:
                return test


class QRCode(Item):
    def __init__(self, width: int, data: str,
                 error_correction: Optional[ERROR_CORRECT_M | ERROR_CORRECT_H | ERROR_CORRECT_Q] = None,
                 box_size: int | None = None, border: int = 0):
        if _QRCode is None:
            raise RuntimeError('No QR code support. Package qrcode is not installed.')
        self._width = width
        self._data = data
        self._error_correction = error_correction
        self._box_size = box_size
        self._border = border

    def render(self) -> Image:
        if self._box_size is None:
            box_size = 2
        else:
            box_size = self._box_size
        probe_box_size = box_size
        qr_image = None
        if self._error_correction is None:
            error_corrections = [ERROR_CORRECT_H, ERROR_CORRECT_Q, ERROR_CORRECT_M, ERROR_CORRECT_L]
        else:
            error_corrections = [self._error_correction]
        error_correction = None
        for error_correction in error_corrections:
            while True:
                logger.debug(f"qrcode: {self._data}, probe_box_size: {probe_box_size}, EC: {error_correction}")
                qr = _QRCode(error_correction=error_correction, box_size=probe_box_size, border=self._border)
                qr.add_data(self._data)
                new_image = qr.make_image()
                if new_image.size[0] <= self._width:
                    qr_image = new_image
                    probe_box_size += 1
                elif qr_image is None:
                    break
                else:
                    break
                if self._box_size is not None:
                    break
            if qr_image:
                break
        if not qr_image:
            raise RuntimeError("Data does not fit in qrcode")

        logger.debug(f"qrcode: {self._data}, final box_size: {probe_box_size - 1}, EC: {error_correction}")

        rest = self._width - qr_image.size[1]
        image = Image.new("1", (qr_image.size[0], self._width), "white")
        image.paste(qr_image, (0, rest // 2))

        return image


class Box(Item):
    def __init__(self, height: int, *items: ItemType, vertical: bool = False, left_padding: int = 0):
        self.height = height
        self.items = items
        self._vertical = vertical
        self._left_padding = left_padding

    def render(self) -> Image:
        rendered_images = [item.render() for item in self.items]
        if self._vertical:
            length = max([rendered_image.size[0] for rendered_image in rendered_images]) + self._left_padding
            assert self.height == sum([rendered_image.size[1] for rendered_image in rendered_images])
            image = Image.new("1", (length, self.height), "white")
            xpos = 0
            for rendered_image in rendered_images:
                image.paste(rendered_image, (self._left_padding, xpos))
                xpos += rendered_image.size[1]
        else:
            length = sum([rendered_image.size[0] for rendered_image in rendered_images]) + self._left_padding
            image = Image.new("1", (length, self.height), "white")
            ypos = self._left_padding
            for rendered_image in rendered_images:
                image.paste(rendered_image, (ypos, 0))
                ypos += rendered_image.size[0]
        return image


class Label(BasePage):
    def __init__(self, item: ItemType):
        self.item = item
        self._bitmap, self._width, self._length = image_to_bitmap(self.item.render())
        self._resolution = Resolution.LOW

        logger.debug(f"label width {self._width}")
        logger.debug(f"label length {self._length}")

        super().__init__()


class Flag(BasePage):
    def __init__(self, item1: ItemType, item2: ItemType, spacing=265):
        rendered_images = [item1.render(), item2.render()]
        image_max_length = max([rendered_image.size[0] for rendered_image in rendered_images])
        length = 2 * image_max_length + spacing
        height = max([rendered_image.size[1] for rendered_image in rendered_images])

        line_length = 2 + spacing % 2
        data = 0x0
        for i in range(height - 1):
            data <<= 1
            if not i % 8:
                data |= 0x01
        b_len = round(height / 8)
        data <<= b_len * 8 - height
        bitmap = line_length * data.to_bytes(b_len, byteorder='big')
        line_image = bitmap_to_image(bitmap, height, line_length)

        white_spacing = (spacing - line_length) // 2

        # spacing_image = Image.new("1", ((spacing - line_length) // 2, height), "white")
        rendered_images.insert(1, line_image)
        positions = [0, image_max_length + white_spacing, line_length + white_spacing]

        image = Image.new("1", (length, height), "white")
        ypos = 0
        for rendered_image, position in zip(rendered_images, positions):
            ypos += position
            image.paste(rendered_image, (ypos, 0))
        self._bitmap, self._width, self._length = image_to_bitmap(image)
        self._resolution = Resolution.LOW

        logger.debug(f"flag width {self._width}")
        logger.debug(f"flag length {self._length}")

        super().__init__()
