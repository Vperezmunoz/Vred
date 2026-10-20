# Enable a pointing ray from a VR controller
# source: enableRay.html

# © 2026 Autodesk, Inc. All rights reserved.

# This example demonstrates how to use enableRay() to display a pointing ray
# from a VR controller and use it to pick objects in the scene.
# 
# enableRay() accepts an axis parameter with possible values:
# "x", "y", "z" - respective axes of the controller's coordinate system
# "custom" - axis of the "Pointer" interaction
# "teleportaxis" - axis of the "Teleport" interaction
# "controllerhandle" - axis through the controller handle
# "leftfinger", "rightfinger" - axes through the left/right index fingers

class Picker:
    def __init__(self):
        # Get the left controller device
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        # Create a custom interaction to trigger the pick action
        self.customInteraction = vrDeviceService.createInteraction("CustomInteraction")
        self.customInteraction.setSupportedInteractionGroups(["CustomGroup"])
        self.released = self.customInteraction.createControllerAction("left-trigger-released")
        self.released.signal().triggered.connect(self.pickWithRay)
        # Limit the interaction to a new mode to not interfere with other interactions
        vrDeviceService.setActiveInteractionGroup("CustomGroup")
        
    def enableRay(self):
        # Enable a pointing ray along the controller handle axis
        self.leftController.enableRay("controllerhandle")

    def disableRay(self):
        # Disable the currently active pointing ray
        self.leftController.disableRay()
        
    def pickWithRay(self):
        # Pick objects in the scene where the ray intersects
        # Returns a vrdRayIntersection with intersection data
        intersection = self.leftController.pick()
        self.printIntersection(intersection)
        
    def printIntersection(self, intersection):
        # Check if the ray hit something and print intersection details
        if intersection.hasHit():
            print("Hit node: " + intersection.getNode().getName())
            print("Hit normal: " + str(intersection.getNormal()))
            print("Origin: " + str(intersection.getOrigin()))
            print("Hit point: " + str(intersection.getPoint()))
            print("Hit UV: " + str(intersection.getUV()))
        else:
            print("No hit")
            
picker = Picker()
picker.enableRay()
