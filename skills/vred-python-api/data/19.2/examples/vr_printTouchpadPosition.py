# Print the current finger position on the touchpad
# source: printTouchpadPosition.html

padPosition = device.getButtonState("Touchpad").getPosition()

# © 2026 Autodesk, Inc. All rights reserved.

class pad:
    def __init__(self):
        self.readPadPosition = False
        self.currentController = ""        

        # Create an intreraction
        self.padInteraction = vrDeviceService.createInteraction("PadInteraction")
        # Set an interaction group that is supported, as other groups already use the touchpad
        self.padInteraction.setSupportedInteractionGroups(["PadMode"])

        # Get the actions that will be used
        self.enableAction = self.padInteraction.createControllerAction("any-touchpad-touched")
        self.disableAction = self.padInteraction.createControllerAction("any-touchpad-untouched")        

        # Connect to the methods that will de-/activate the reading of the touchpad position
        # and the actual printing
        self.enableAction.signal().triggered.connect(self.enablePad)
        self.disableAction.signal().triggered.connect(self.disablePad)        

        # Set the interaction group active
        vrDeviceService.setActiveInteractionGroup("PadMode")

    def printPosition(self, device):                
        # Get the position of the finger on the touchpad and print it
        padPosition = device.getButtonState("Touchpad").getPosition()
        print(("Touchpad position: " + str(padPosition.x()) + " " + str(padPosition.y())))

    def enablePad(self, action, device):                
        # If position reading is already active, do not do anything
        if self.readPadPosition:
            return

        # Store which controller is currently used
        self.currentController = device.getName()
        # Activate the reading
        self.readPadPosition = True
        device.signal().moved.connect(self.printPosition)

    def disablePad(self, action, device):
        # If position reading is not active, do not do anything
        if not self.readPadPosition:
            return

        # Check if this is the controller that activated the position printing
        if self.currentController != device.getName():
            return
        
        # Deactivate the position reading and printing
        self.readPadPosition = False
        device.signal().moved.disconnect(self.printPosition)
    
thePad = pad()
