# Set the default teleport to a virtual button.
# source: setTeleportToVirtualButton.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get the left controller
leftController = vrDeviceService.getVRDevice("left-controller")
# Get the right controller
rightController = vrDeviceService.getVRDevice("right-controller")

# Define the description of the virtual buttons on the touchpad.
# These description consist of a name, a radius 0 - 1 and an angle 0 - 360, 
# where on the circular touchpad the button is located
padCenter = vrdVirtualTouchpadButton("padcenter", 0.0, 0.5, 0.0, 360.0)
padLeft = vrdVirtualTouchpadButton("padleft", 0.5, 1.0, 225.0, 315.0)
padUp = vrdVirtualTouchpadButton("padup", 0.5, 1.0, 315.0, 45.0)
padRight = vrdVirtualTouchpadButton("padright", 0.5, 1.0, 45.0, 135.0)
padDown = vrdVirtualTouchpadButton("paddown", 0.5, 1.0, 135.0, 225.0)

# Add the descirptions for the virtual buttons to the left controller
leftController.addVirtualButton(padCenter, "touchpad")
leftController.addVirtualButton(padLeft, "touchpad")
leftController.addVirtualButton(padUp, "touchpad")
leftController.addVirtualButton(padRight, "touchpad")
leftController.addVirtualButton(padDown, "touchpad")

# Also add the descriptions to the right controller
# Note that each controller can have different tochpad layouts, if
# it is needed.
rightController.addVirtualButton(padLeft, "touchpad")
rightController.addVirtualButton(padUp, "touchpad")
rightController.addVirtualButton(padRight, "touchpad")
rightController.addVirtualButton(padDown, "touchpad")
rightController.addVirtualButton(padCenter, "touchpad")

# Get the interaction which actions should be remapped to the virtual buttons
teleport = vrDeviceService.getInteraction("Teleport")
# Set the mapping of the actions to the new virtual buttons
teleport.setControllerActionMapping("prepare", "any-paddown-touched")
teleport.setControllerActionMapping("abort", "any-paddown-untouched")
teleport.setControllerActionMapping("execute", "any-paddown-pressed")
