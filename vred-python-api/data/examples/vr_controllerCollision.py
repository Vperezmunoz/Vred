# Connecting to a signal that is executed, when the controller collides with a node
# source: controllerCollision.html

# © 2026 Autodesk, Inc. All rights reserved.

def onCollisionStarted(node, device):
    print("Collision started")
    device.vibrate(250, 0)

def onCollisionStopped(node, device):
    print("Collision stopped")
    device.vibrate(250, 0)

rightController = vrDeviceService.getVRDevice("right-controller")
leftController = vrDeviceService.getVRDevice("left-controller")

rightController.signal().collisionStarted.connect(onCollisionStarted)
rightController.signal().collisionStopped.connect(onCollisionStopped)

leftController.signal().collisionStarted.connect(onCollisionStarted)
leftController.signal().collisionStopped.connect(onCollisionStopped)
