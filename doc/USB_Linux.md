# USB

## LibUSB

libusb - Check Linux/Windows install Guides for this

- On Ubuntu this is likely already installed.

## Permissions

If you are on Linux, you may need to add a UDEV Rule to allow the Printer to be accessed by your User.

Rule: `/etc/udev/rules.d/99-brother-ptp700.rules`

```bash
SUBSYSTEMS=="usb", GROUP="plugdev", ACTION=="add", ATTRS{idVendor}==<VENDOR_ID>, ATTRS{idProduct}==<PRODUCT_ID>, MODE="0660"
```

This sets the owner of the device node to root:usbusers rather than root:root

Ensure that the User is in the `plu gdev` group : `sudo usermod -aG plugdev <USER>`

## Brother P-Touch

Note: If your printer has a 'PLite' mode, you need to disable it if you want to print via USB. Make sure that the corresponding LED is not lit by holding the button down until it turns off.

Get VendorID : `lsusb | grep -i Brother | awk '{print $6}' | cut -d':' -f1`

Get ProductID: `lsusb | grep -i Brother | awk '{print $6}' | cut -d':' -f2`
