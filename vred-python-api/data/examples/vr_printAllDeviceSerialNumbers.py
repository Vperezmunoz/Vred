# Print the serial number of all connected devices
# source: printAllDeviceSerialNumbers.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get all currently connected VR devices
devices = vrDeviceService.getConnectedVRDevices()

# Print name and serial number for all devices
# Note: If a VR device is created in a script before it is connected, 
# name or serial number may be empty
for device in devices:
    print((device.getName()))
    print((device.getSerialNumber()))
