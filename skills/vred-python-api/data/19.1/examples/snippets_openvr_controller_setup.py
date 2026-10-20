# (Deprecated) openvr_controller_setup
# source: openvr_controller_setup.html

# © 2026 Autodesk, Inc. All rights reserved.

# Deprecated. See vr/customInteraction.py, vr/printTouchparPosition.py, vr/virtualControllerButtons.py instead.
def trigger0Pressed():
    controller0.setPickingAxis(0)
    controller0.showPickingAxis(true)

def trigger0Released():
    pickedNode = controller0.pickNode()
    selectNode(pickedNode)
    controller0.showPickingAxis(false)

def grip0Pressed():
    selectNode(getSelectedNode(), false)

def grip0Released():
    print("grip0Released")

def touchpad0Pressed():
    print("touchpad0Pressed")

def touchpad0Released():
    print("touchpad0Released")

def touchpad0PositionChanged(position):
    print("touchpad0PositionChanged")

def controller0Moved():
    if controller0.isTouchpadPressed():
        leftNode = findNode("MatrixLeft")
        leftNode.setTransformMatrix( controller0.getWorldMatrix(), false)

def trigger1Pressed():
    controller1.setPickingAxis(1)
    controller1.showPickingAxis(true)


def trigger1Released():
    pickedNode = controller1.pickNode()
    selectNode(pickedNode)
    controller1.showPickingAxis(false)

def grip1Pressed():
    selectNode(getSelectedNode(), false)


def grip1Released():
    print("grip1Released")

def touchpad1Pressed():
    print("touchpad1Pressed")


def touchpad1Released():
    print("touchpad1Released")

def touchpad1PositionChanged(position):
    print("touchpad1PositionChanged")

def controller1Moved():
    if controller1.isTouchpadPressed():
        rightNode = findNode("MatrixRight")
        rightNode.setTransformMatrix( controller1.getWorldMatrix(), false)

##
## Create two controller and connect their signals to functions as needed
##

controller0 = vrOpenVRController("Controller0")
controller0.connectSignal("controllerMoved", controller0Moved)
controller0.connectSignal("triggerPressed", trigger0Pressed)
controller0.connectSignal("triggerReleased", trigger0Released)
controller0.connectSignal("gripPressed", grip0Pressed)


controller1 = vrOpenVRController("Controller1")
controller1.connectSignal("controllerMoved", controller1Moved)
controller1.connectSignal("triggerPressed", trigger1Pressed)
controller1.connectSignal("triggerReleased", trigger1Released)
controller1.connectSignal("gripPressed", grip1Pressed)


##
## Optional connect more signals
##
#controller0.connectSignal("gripReleased", grip0Released)
#controller0.connectSignal("touchpadPressed", touchpad0Pressed)
#controller0.connectSignal("touchpadReleased", touchpad0Released)
#controller0.connectSignal("touchpadPositionChanged", touchpad0PositionChanged)
#controller1.connectSignal("gripReleased", grip1Released)
#controller1.connectSignal("touchpadPressed", touchpad1Pressed)
#controller1.connectSignal("touchpadReleased", touchpad1Released)
#controller1.connectSignal("touchpadPositionChanged", touchpad1PositionChanged)

##
## In case the scene origin is not located at 0,0,0 you may set a reference origin instead
##
setOpenVRTrackingOrigin( Pnt3f(0.0, 0.0, 0.0))
