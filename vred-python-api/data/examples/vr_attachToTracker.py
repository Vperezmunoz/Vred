# Add a child node to the node of a VR Tracker
# source: attachToTracker.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get the first tracker
tracker = vrDeviceService.getVRDevice("tracker-1")

# Create a red box
box = createNode("Transform3D", "TrackerBox", False)
box.addChild(createBox(100, 100, 100, 1, 1, 1, 1.0, 0.0, 0.0, 0.0))

# Attach the box to the tracker
constraint = vrConstraintService.createParentConstraint([tracker.getNode()], box, False)
