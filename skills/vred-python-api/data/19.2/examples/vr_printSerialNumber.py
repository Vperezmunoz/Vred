# Print the serial number of a device
# source: printSerialNumber.html

# © 2026 Autodesk, Inc. All rights reserved.

# Print the serial number of a device
def printSerialNumber(action, device):
    print((device.getSerialNumber()))

# Get an interaction of which an action signal can be used
pointer = vrDeviceService.getInteraction("Pointer")
# Get an action
prepare = pointer.getControllerAction("prepare")
# Connect the method to print the serial number to the signal of the action
prepare.signal().triggered.connect(printSerialNumber)
