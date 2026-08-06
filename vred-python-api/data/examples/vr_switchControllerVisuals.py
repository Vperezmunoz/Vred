# Switch the visualization mode of a VR device
# source: switchControllerVisuals.html

# © 2026 Autodesk, Inc. All rights reserved.

# Get the left controller
leftController = vrDeviceService.getVRDevice("left-controller")
# Get the right controller
rightController = vrDeviceService.getVRDevice("right-controller")
# Get the first connected tracker
tracker = vrDeviceService.getVRDevice("tracker-1")

# Set left controller visualization to controller with hand
leftController.setVisualizationMode(Visualization_ControllerAndHand)
# Set right controller visualization to controller
rightController.setVisualizationMode(Visualization_Hand)
# Set the trackers visualization to controller, which in this case will
# display a tracker visualization
tracker.setVisualizationMode(Visualization_Controller)
