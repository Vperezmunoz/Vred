# Connect to signals of device actions
# source: connectToDeviceActionSignal.html

# © 2026 Autodesk, Inc. All rights reserved.

# Simple function that should be called when an action is executed
def pointerPrepare(action, device):
    print("Pointer prepare")

# Get the interaction that holds the action, the function should be connected to
pointer = vrDeviceService.getInteraction("Pointer")
# Get the interaction's action
prepare = pointer.getControllerAction("prepare")
# Connect the function to the actual signal of the action's signal object
prepare.signal().triggered.connect(pointerPrepare)
