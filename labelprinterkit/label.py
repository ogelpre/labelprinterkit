"""
Labels are the Base class you derive your Labels from. A few simple Labels are
provided for you.
"""
from typing import Tuple

from PIL import Image


def _coord_add(tup1, tup2):
    """add two tuples of size two"""
    return (tup1[0] + tup2[0], tup1[1] + tup2[1])


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
        width = max([ img.size[1] for img in limg ])

        img = Image.new("1", (height, width), "white")
        for i, l in enumerate(limg):
            img.paste(l,(int(i*h),0))

        return img

# print("".join(f"{x:08b}".replace("0", " ") for x in bytes(i)))
