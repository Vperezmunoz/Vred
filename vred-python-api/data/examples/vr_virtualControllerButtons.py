# Define and use virtual buttons on the touchpad of a VR controller
# source: virtualControllerButtons.html

# © 2026 Autodesk, Inc. All rights reserved.

# Define actions as python functions
class VirtualPad:

    def __init__(self):
        # Get the left controller
        self.leftController = vrDeviceService.getVRDevice("left-controller")

        # Define several buttons on the touchpad
        self.padCenter = vrdVirtualTouchpadButton("padcenter", 0.0, 0.5, 0.0, 360.0)
        self.padLeft = vrdVirtualTouchpadButton("padleft", 0.5, 1.0, 225.0, 315.0)
        self.padUp = vrdVirtualTouchpadButton("padup", 0.5, 1.0, 315.0, 45.0)
        self.padRight = vrdVirtualTouchpadButton("padright", 0.5, 1.0, 45.0, 135.0)
        self.padDown = vrdVirtualTouchpadButton("paddown", 0.5, 1.0, 135.0, 225.0)

        # Add the virtual buttons to the controller
        self.leftController.addVirtualButton(self.padCenter, "touchpad")
        self.leftController.addVirtualButton(self.padLeft, "touchpad")
        self.leftController.addVirtualButton(self.padUp, "touchpad")
        self.leftController.addVirtualButton(self.padRight, "touchpad")
        self.leftController.addVirtualButton(self.padDown, "touchpad")

        # Create new interaction
        self.multiButtonPad = vrDeviceService.createInteraction("MultiButtonPad")
        # Limit the interaction to a new mode to not interfere with other interactions
        self.multiButtonPad.setSupportedInteractionGroups(["VirtualButtons"])

        # Create action objects that a triggered by some input
        self.leftAction = self.multiButtonPad.createControllerAction("left-padleft-pressed")
        self.upAction = self.multiButtonPad.createControllerAction("left-padup-pressed")
        self.rightAction = self.multiButtonPad.createControllerAction("left-padright-pressed")
        self.downAction = self.multiButtonPad.createControllerAction("left-paddown-pressed")
        self.centerAction = self.multiButtonPad.createControllerAction("left-padcenter-pressed")

        # Connect these actions to the actual python functions
        self.leftAction.signal().triggered.connect(self.left)
        self.upAction.signal().triggered.connect(self.up)
        self.rightAction.signal().triggered.connect(self.right)
        self.downAction.signal().triggered.connect(self.down)
        self.centerAction.signal().triggered.connect(self.center)

        # Activate the mode that supports the new interaction
        vrDeviceService.setActiveInteractionGroup("VirtualButtons")

    def left(self, action, device):
        print("left")

    def up(self, action, device):
        print("up")

    def right(self, action, device):
        print("right")

    def down(self, action, device):
        print("down")

    def center(self, action, device):
        print("center")

pad = VirtualPad()
