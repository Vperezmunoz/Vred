# Combine a custom and a default device interaction
# source: combineCustomAndDefaultInteraction.html

teleport = vrDeviceService.getInteraction("Teleport")
teleport.addSupportedInteractionGroup("CustomGroup")

teleport.setControllerActionMapping("prepare", "right-customtrigger-touched")
teleport.setControllerActionMapping("abort", "right-customtrigger-untouched")
teleport.setControllerActionMapping("execute", "right-customtrigger-pressed")

# © 2026 Autodesk, Inc. All rights reserved.

# Define actions as python functions
class ExampleInteraction:
    def __init__(self):
        self.active = False
        # Create new interaction
        self.customInteraction = vrDeviceService.createInteraction("CustomInteraction")
        # Limit the interaction to a new mode to not interfere with other interactions
        self.customInteraction.setSupportedInteractionGroups(["CustomGroup"])

        # Create action objects that a triggered by some input
        self.pressed = self.customInteraction.createControllerAction("left-trigger-pressed")
        self.released = self.customInteraction.createControllerAction("left-trigger-released")        

        # Connect these actions to the actual python functions
        self.pressed.signal().triggered.connect(self.pressMethod)
        self.released.signal().triggered.connect(self.releaseMethod)         

        # Get the teleport interaction and add the interaction group
        teleport = vrDeviceService.getInteraction("Teleport")
        teleport.addSupportedInteractionGroup("CustomGroup")
        teleport.setControllerActionMapping("prepare", "right-customtrigger-touched")
        teleport.setControllerActionMapping("abort", "right-customtrigger-untouched")
        teleport.setControllerActionMapping("execute", "right-customtrigger-pressed")

        # Activate the mode that supports the new interaction
        vrDeviceService.setActiveInteractionGroup("CustomGroup")    

    def pressMethod(self, action, device):
        print("Press")
        self.active = True
        device.signal().moved.connect(self.moveMethod)

    def releaseMethod(self, action, device):
        print("Release")
        self.active = False
        device.signal().moved.disconnect(self.moveMethod)

    def moveMethod(self, device):
        print("Move")        

interaction = ExampleInteraction()
