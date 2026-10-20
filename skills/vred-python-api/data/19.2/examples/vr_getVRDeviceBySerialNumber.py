# Get a VR device by its serial number
# source: getVRDeviceBySerialNumber.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get tracker by its serial number
tracker1 = vrDeviceService.getVRDeviceBySerialNumber("LHR-0DDDBBF0")

# Create a red box
box = createBox(100, 100, 100, 1, 1, 1, 1.0, 0.0, 0.0, 0.0)

# Attach the box to the tracker
tracker1.getNode().children.append(box)
