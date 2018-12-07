"""
Labels are the Base class you derive your Labels from. A few simple Labels are
provided for you.
"""
from typing import Tuple

from PIL import Image


class Label:
    def __init__(self, *items):
        self.items = items
        if not self.items:
            raise ValueError(
                "A Labels 'items' attribute must contain a list of "
                "renderable objects")

    def render(self, height) -> Image:
        """render the Label.

        Args:
            height: Height request
        """

        h = height/len(self.items)
        limg = [ item.render(h) for item in self.items ]
        width = max([ img.size[0] for img in limg ])

        img = Image.new("1", (width, height), "white")
        for i, l in enumerate(limg):
            img.paste(l, (0, int(i*h)))

        return img


class ImageLabel:
    def __init__(self, path):
        self.path = path

    def render(self, height):
        image = Image.open(self.path)
        ow, oh = image.size
        w = int(ow*oh/128)
        resimg =  image.resize((w,128))
        img = Image.new("1", (w, 128), "white")
        img.paste(resimg)

        return img
