"""
Objects that can be placed in a label template
"""

from PIL import Image, ImageDraw, ImageFont
from math import ceil

class Text:
    """A simple text item"""
    def __init__(self, text, font_path='comic.ttf', **kwargs) -> None:
        self.text = text
        self.font_path = font_path

        self.pad_top = kwargs.get("pad_top", 0)
        self.pad_right = kwargs.get("pad_right", 0)
        self.pad_bottom = kwargs.get("pad_bottom", 0)
        self.pad_left = kwargs.get("pad_left", 0)

    def render(self, height):
        iheight = height - self.pad_top - self.pad_bottom
        font_size = self._calc_font_size(iheight)
        font = ImageFont.truetype(self.font_path, font_size)
        text_x, text_y = font.getsize(self.text)
        padded_size = (
            text_x + self.pad_left + self.pad_right,
            text_y + self.pad_top + self.pad_bottom,
        )
        image = Image.new("1", padded_size, "white")
        draw = ImageDraw.Draw(image)
        draw.text((self.pad_left, self.pad_top), self.text, "black", font)
        return image

    def _calc_font_size(self, height):
        lower = 1
        upper = 1
        while True:
            font = ImageFont.truetype(self.font_path, upper)
            if font.getsize(self.text)[1] >= height:
                break
            lower = upper
            upper *= 2
        while True:
            test = ceil((upper+lower)/2)
            font = ImageFont.truetype(self.font_path, test)
            font_height = font.getsize(self.text)[1]
            if upper - lower <= 1:
                return lower
            elif font_height > height:
                upper = test
            elif font_height < height:
                lower = test
            else:
                return test

