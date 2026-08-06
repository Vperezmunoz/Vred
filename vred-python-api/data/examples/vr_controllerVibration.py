# Triggering the vibration functionality of a controller
# source: controllerVibration.html

# © 2026 Autodesk, Inc. All rights reserved.

class ControllerFeedback:
    def __init__(self):
        self.vibrationDuration = 250
        self.vibrationAxis = 0
        # Attach controller to a signal to trigger the actual vibration
        pointer = vrDeviceService.getInteraction("Pointer")
        executeAction = pointer.getControllerAction("execute")
        executeAction.signal().triggered.connect(self.vibrate)
    
    def vibrate(self, action, device):
        # Let a controller axis vibrate for a certain amount of time.
        # Note: Most controllers only support one axis with id 0.
        device.vibrate(self.vibrationDuration, self.vibrationAxis)

feedback = ControllerFeedback()
