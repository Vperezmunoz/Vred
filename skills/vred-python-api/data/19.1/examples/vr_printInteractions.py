# Print out all available device interactions
# source: printInteractions.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get all registered interactions
interactions = vrDeviceService.getInteractions()

# Print out all interaction names
for interaction in interactions:
    print((interaction.getName()))
