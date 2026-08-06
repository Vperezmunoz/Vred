# Print device actions of a device interaction
# source: printActions.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get an interaction for which the actions should be printed out
teleport = vrDeviceService.getInteraction("Teleport")
# Get all actions of the interaction
actions = teleport.getControllerActions()

# Print all action names
for action in actions:
    print((action.getName()))
