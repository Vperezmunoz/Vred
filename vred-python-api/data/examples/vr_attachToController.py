# Add a child node to the node of a VR Controller
# source: attachToController.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get left controller
leftController = vrDeviceService.getVRDevice("left-controller")
# Get right controller
rightController = vrDeviceService.getVRDevice("right-controller")

# Create a red box
leftBox = createNode("Transform3D", "LeftBox", False)
leftBox.addChild(createBox(100, 100, 100, 1, 1, 1, 1.0, 0.0, 0.0, 0.0))
# Create a blue box
rightBox = createNode("Transform3D", "RightBox", False)
rightBox.addChild(createBox(100, 100, 100, 1, 1, 1, 0.0, 0.0, 1.0, 0.0))

# Atttach the boxes to the controllers
leftConstraint = vrConstraintService.createParentConstraint([leftController.getNode()], leftBox, False)
rightConstraint = vrConstraintService.createParentConstraint([rightController.getNode()], rightBox, False)
