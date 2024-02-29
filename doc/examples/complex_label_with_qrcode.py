# This example creates a more complex label with a QR Code and two text lines.
#
# The label will look like this sketch:
#
# +-------+------------------+
# |  QR   | Text 1           |
# | Code  +------------------+
# |       | Text 2           |
# +-------+------------------+
#

# First let's import all the needed Classes

from labelprinterkit.backends.network import TCPBackend
from labelprinterkit.constants import Media
from labelprinterkit.job import Job
from labelprinterkit.label import Label, Box, Text, QRCode, Padding
from labelprinterkit.printers.P750W import P750W

# The label will be created for a 12mm band. The 12mm has 70 pixel/points width.
# So let's create a QR code with 70 pixels width.
qrcode = QRCode(70, "https://pypi.org/project/labelprinterkit/")

# Create text for the label
# The upper text is 25 pixels height and the lower text is 45 pixels height.
# Both together have the 70 points width of the label.
# The lower label gets 1 pixel padding on the top for some spacing.
# If the font_size is not given, the font_size is calculated automatically to fit in the width
text1 = Text(25, "This label is proudly presented by", 'comic.ttf')
text2 = Text(45, "labelprinterkit", 'comic.ttf', padding=Padding(0, 1, 0, 0))

# Insert Text into boxes, add left_padding to get some space to the qr code
right_box = Box(70, text1, text2, vertical=True, left_padding=10)

# Now we can put the qrcode and the box with text together
full_box = Box(70, qrcode, right_box)

# Create label with box from above
label = Label(full_box)

# For debugging purpose you can render an PIL image from the label and save it
label.image.save('/tmp/label.png')

# Create job with configuration and add label as page
job = Job(Media.TZE_12)
job.add_page(label)

# Use TCP backend to connect to printer
backend = TCPBackend('labelprinter-1.example.com')
printer = P750W(backend)

# Print job
printer.print(job)
