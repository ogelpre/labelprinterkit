#!/usr/bin/env python3

from labelprinterkit.label import Label
from labelprinterkit.items import Text
from labelprinterkit.backends import PyUSBBackend
from labelprinterkit.printers.brother_pt700 import P700

#from PIL import ImageFont
#font = ImageFont.truetype("FreeSans.ttf", 60)

backend = PyUSBBackend.auto()
printer = P700(backend)

l = Label(Text("gX|"))
#print(printer.get_status())
printer.print_label(l)
