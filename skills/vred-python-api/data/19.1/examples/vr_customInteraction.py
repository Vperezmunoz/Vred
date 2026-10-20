# Implementation of a custom device interaction
# source: customInteraction.html

self.customInteraction = vrDeviceService.createInteraction("CustomInteraction")

self.customInteraction.setSupportedInteractionGroups(["CustomGroup"])

self.grabAction = self.customInteraction.createControllerAction("left-trigger-pressed")
self.releaseAction = self.customInteraction.createControllerAction("left-trigger-released")

self.grabAction.signal().triggered.connect(self.press)
self.releaseAction.signal().triggered.connect(self.release)

vrDeviceService.setActiveInteractionGroup("CustomGroup")

device.signal().moved.connect(self.move)

# © 2026 Autodesk, Inc. All rights reserved.

# Define actions as python functions
class MyCustomInteraction:
    def __init__(self):
        # Create new interaction
        self.customInteraction = vrDeviceService.createInteraction("CustomInteraction")
        # Limit the interaction to a new mode to not interfere with other interactions
        self.customInteraction.setSupportedInteractionGroups(["CustomGroup"])

        # Create action objects that a triggered by some input
        self.grabAction = self.customInteraction.createControllerAction("left-trigger-pressed")
        self.releaseAction = self.customInteraction.createControllerAction("left-trigger-released")        

        # Connect these actions to the actual python functions
        self.grabAction.signal().triggered.connect(self.press)
        self.releaseAction.signal().triggered.connect(self.release)        

        # Activate the mode that supports the new interaction
        vrDeviceService.setActiveInteractionGroup("CustomGroup")
    
    def press(self, action, device):
        print("press")
        device.signal().moved.connect(self.move)

    def release(self, action, device):
        print("release")
        device.signal().moved.disconnect(self.move)

    def move(self, device):
        print("move")

myCustomInteraction = MyCustomInteraction()
