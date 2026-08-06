# (Deprecated) Oculus touch example
# source: OculusTouchExample.html

## Example on how to setup the oculus touch controller
## Any print calls should be avoided in a real world scenario
## since the can limit performance a lot
from math import sqrt

## find and remember the Controller nodes.
## it should be avoided to call findNode often since it can
## slow down rendering quite a bit
leftNode = findNode("MatrixLeft")
rightNode = findNode("MatrixRight")

## Controller Movement
def leftControllerMoved():
    leftNode.setTransformMatrix( leftController.getWorldMatrix(), false)

def rightControllerMoved():
    rightNode.setTransformMatrix( rightController.getWorldMatrix(), false)

## Button presses
def buttonXPressed():
    print "button X pressed"
    leftController.setPickingAxis(0)
    leftController.showPickingAxis(true)


def buttonXReleased():
    print "button X released"
    leftController.setPickingAxis(0)
    leftController.showPickingAxis(false)


def buttonXIsPressed():
    print "button X is pressed "

def buttonXTouched():
    print "button X touched"

def buttonXUntouched():
    print "button X untouched"

def buttonXIsTouched():
    print "button X is touched"

def buttonYPressed():
    print "button Y pressed"
    leftController.setPickingAxis(1)
    leftController.showPickingAxis(true)


def buttonYReleased():
    print "button Y released"
    leftController.setPickingAxis(1)
    leftController.showPickingAxis(false)
    leftNode.setActive(false); # hide the controller so it is not picked
    selectNode(leftController.pickNode())
    leftNode.setActive(true); # unhide the controller so it is not picked

def buttonYIsPressed():
    print "button Y is pressed "

def buttonYTouched():
    print "button Y touched"

def buttonYUntouched():
    print "button Y untouched"

def buttonYIsTouched():
    print "button Y is touched"

def buttonAPressed():
    print "button A pressed"
    rightController.setPickingAxis(2)
    rightController.showPickingAxis(true)

def buttonAReleased():
    print "button A released"
    rightController.setPickingAxis(2)
    rightController.showPickingAxis(false)


def buttonAIsPressed():
    print "button A is pressed"

def buttonATouched():
    print "button A touched"

def buttonAUntouched():
    print "button A untouched"

def buttonAIsTouched():
    print "button A is touched"

def buttonBPressed():
    print "button B pressed"
    rightController.setPickingAxis(3)
    rightController.showPickingAxis(true)

def buttonBReleased():
    print "button B released"
    rightController.setPickingAxis(3)
    rightController.showPickingAxis(false)
    rightNode.setActive(false); # hide the controller so it is not picked
    selectNode(rightController.pickNode())
    rightNode.setActive(true); # unhide the controller so it is not picked

def buttonBIsPressed():
    print "button B is pressed "

def buttonBTouched():
    print "button B touched"

def buttonBUntouched():
    print "button B untouched"

def buttonBIsTouched():
    print "button B is touched"

## Thumbsticks
def leftThumbstickPressed():
    print("leftThumbstick pressed")

def leftThumbstickReleased():
    print("leftThumbstick released")

def leftThumbstickIsPressed():
    print("leftThumbstick is pressed")

def leftThumbstickTouched():
    print "leftThumbstick touched"

def leftThumbstickUntouched():
    print "leftThumbstick untouched"

def leftThumbstickIsTouched():
    print "leftThumbstick is touched"

def leftThumbstickChanged(position):
    #print "left Thumbstick PositionChanged"
    oldPos = getOculusRiftTrackingOrigin()
    touchPos = leftController.getThumbstickPosition()
    scaleFactor = 25.0
    #moveScaleForward = scaleFactor * touchPos.y()
    #moveScaleSideways = scaleFactor * touchPos.x()
    #camDirForward = getNormalizedDirection( getCamNode(-1).getWorldTransform())
    #camDirSideways = Vec2f( -camDirForward.y(), camDirForward.x())
    #newPos = Pnt3f(oldPos.x() + moveScaleForward * camDirForward.x() + moveScaleSideways * camDirSideways.x(), oldPos.y(), oldPos.z() + moveScaleForward*camDirForward.y() + moveScaleSideways * camDirSideways.y())
    newPos = Pnt3f( oldPos.x() + scaleFactor * touchPos.x(), oldPos.y(), oldPos.z() + scaleFactor * touchPos.y());
    setOculusRiftTrackingOrigin(newPos)

def rightThumbstickPressed():
    print("rightThumbstick pressed")

def rightThumbstickReleased():
    print("rightThumbstick released")

def rightThumbstickIsPressed():
    print("rightThumbstick is pressed")

def rightThumbstickTouched():
    print "rightThumbstick touched"

def rightThumbstickUntouched():
    print "rightThumbstick untouched"

def rightThumbstickIsTouched():
    print "rightThumbstick is touched"

def rightThumbstickChanged(position):
    print "rightThumbstick PositionChanged"
    print position

## Trigger
def leftTriggerPressed():
    print "left trigger"

def leftTriggerReleased():
    print "left trigger released"

def leftTriggerIsPressed():
    print "left trigger is pressed"

def leftTriggerTouched():
    print "leftTrigger touched"

def leftTriggerUntouched():
    print "leftTrigger untouched"

def leftTriggerIsTouched():
    print "leftTrigger is touched"

def leftTriggerChanged(value):
    print "leftTriggerChanged "
    print value

def rightTriggerPressed():
    print "right trigger"

def rightTriggerReleased():
    print "right trigger released"

def rightTriggerIsPressed():
    print "right trigger is pressed"

def rightTriggerTouched():
    print "rightTrigger touched"

def rightTriggerUntouched():
    print "rightTrigger untouched"

def rightTriggerIsTouched():
    print "rightTrigger is touched"

def rightTriggerChanged(value):
    print "rightTriggerChanged "
    print value

## Hand Trigger (Grip)
def leftHandTriggerPressed():
    print "left hand trigger"

def leftHandTriggerReleased():
    print "left hand trigger released"

def leftHandTriggerIsPressed():
    print "left hand trigger is pressed"

def leftHandTriggerChanged(value):
    print "leftHandTriggerChanged "
    leftController.triggerVibration(1.0, value)

def rightHandTriggerPressed():
    print "right hand trigger"

def rightHandTriggerReleased():
    print "right hand trigger released"

def rightHandTriggerIsPressed():
    print "right hand trigger is pressed"

def rightHandTriggerChanged(value):
    print "rightHandTriggerChanged "
    rightController.triggerVibration(0.5, value)

def getNormalizedDirection(matrix):
    inVec = Vec2f( -matrix[2], matrix[6])
    rescale = 1.0 / sqrt( inVec.x()*inVec.x() + inVec.y() * inVec.y())
    return Vec2f( inVec.x() * rescale, inVec.y() * rescale)

## Thumb Rest
def leftThumbRestTouched():
    print "leftThumbRest touched"

def leftThumbRestUntouched():
    print "leftThumbRest untouched"

def leftThumbRestIsTouched():
    print "leftThumbRest is touched"

def rightThumbRestTouched():
    print "rightThumbRest touched"

def rightThumbRestUntouched():
    print "rightThumbRest untouched"

def rightThumbRestIsTouched():
    print "rightThumbRest is touched"

##
## Create two controller and connect their signals to functions as needed
##

#
## Left controller, must be namend LeftTouch
leftController = vrOculusTouchController("LeftTouch")
leftController.connectSignal("controllerMoved", leftControllerMoved)
leftController.connectSignal("button0Pressed", buttonXPressed)
leftController.connectSignal("button0Released", buttonXReleased)
leftController.connectSignal("button0IsPressed", buttonXIsPressed)
leftController.connectSignal("button0Touched", buttonXTouched)
leftController.connectSignal("button0Untouched", buttonXUntouched)
leftController.connectSignal("button0IsTouched", buttonXIsTouched)

leftController.connectSignal("button1Pressed", buttonYPressed)
leftController.connectSignal("button1Released", buttonYReleased)
leftController.connectSignal("button1IsPressed", buttonYIsPressed)
leftController.connectSignal("button1Touched", buttonYTouched)
leftController.connectSignal("button1Untouched", buttonYUntouched)
leftController.connectSignal("button1IsTouched", buttonYIsTouched)

leftController.connectSignal("thumbstickPressed", leftThumbstickPressed)
leftController.connectSignal("thumbstickReleased", leftThumbstickReleased)
leftController.connectSignal("thumbstickIsPressed", leftThumbstickIsPressed)
leftController.connectSignal("thumbstickTouched", leftThumbstickTouched)
leftController.connectSignal("thumbstickUntouched", leftThumbstickUntouched)
leftController.connectSignal("thumbstickIsTouched", leftThumbstickIsTouched)
leftController.connectSignal("thumbstickChanged", leftThumbstickChanged)

leftController.connectSignal("thumbRestTouched", leftThumbRestTouched)
leftController.connectSignal("thumbRestUntouched", leftThumbRestUntouched)
leftController.connectSignal("thumbRestIsTouched", leftThumbRestIsTouched)

leftController.connectSignal("triggerPressed", leftTriggerPressed)
leftController.connectSignal("triggerReleased", leftTriggerReleased)
leftController.connectSignal("triggerIsPressed", leftTriggerIsPressed)
leftController.connectSignal("triggerTouched", leftTriggerTouched)
leftController.connectSignal("triggerUntouched", leftTriggerUntouched)
leftController.connectSignal("triggerIsTouched", leftTriggerIsTouched)
leftController.connectSignal("triggerChanged", leftTriggerChanged)

leftController.connectSignal("handTriggerPressed", leftHandTriggerPressed)
leftController.connectSignal("handTriggerReleased", leftHandTriggerReleased)
leftController.connectSignal("handTriggerIsPressed", leftHandTriggerIsPressed)
leftController.connectSignal("handTriggerChanged", leftHandTriggerChanged)



## Right controller, must be namend RightTouch
rightController = vrOculusTouchController("RightTouch")
rightController.connectSignal("controllerMoved", rightControllerMoved)

rightController.connectSignal("button0Pressed", buttonAPressed)
rightController.connectSignal("button0Released", buttonAReleased)
rightController.connectSignal("button0IsPressed", buttonAIsPressed)
rightController.connectSignal("button0Touched", buttonATouched)
rightController.connectSignal("button0Untouched", buttonAUntouched)
rightController.connectSignal("button0IsTouched", buttonAIsTouched)

rightController.connectSignal("button1Pressed", buttonBPressed)
rightController.connectSignal("button1Released", buttonBReleased)
rightController.connectSignal("button1IsPressed", buttonBIsPressed)
rightController.connectSignal("button1Touched", buttonBTouched)
rightController.connectSignal("button1Untouched", buttonBUntouched)
rightController.connectSignal("button1IsTouched", buttonBIsTouched)


rightController.connectSignal("thumbstickPressed", rightThumbstickPressed)
rightController.connectSignal("thumbstickReleased", rightThumbstickReleased)
rightController.connectSignal("thumbstickIsPressed", rightThumbstickIsPressed)
rightController.connectSignal("thumbstickTouched", rightThumbstickTouched)
rightController.connectSignal("thumbstickUntouched", rightThumbstickUntouched)
rightController.connectSignal("thumbstickIsTouched", rightThumbstickIsTouched)
rightController.connectSignal("thumbstickChanged", rightThumbstickChanged)

rightController.connectSignal("thumbRestTouched", rightThumbRestTouched)
rightController.connectSignal("thumbRestUntouched", rightThumbRestUntouched)
rightController.connectSignal("thumbRestIsTouched", rightThumbRestIsTouched)

rightController.connectSignal("triggerPressed", rightTriggerPressed)
rightController.connectSignal("triggerReleased", rightTriggerReleased)
rightController.connectSignal("triggerIsPressed", rightTriggerIsPressed)
rightController.connectSignal("triggerTouched", rightTriggerTouched)
rightController.connectSignal("triggerUntouched", rightTriggerUntouched)
rightController.connectSignal("triggerIsTouched", rightTriggerIsTouched)
rightController.connectSignal("triggerChanged", rightTriggerChanged)

rightController.connectSignal("handTriggerPressed", rightHandTriggerPressed)
rightController.connectSignal("handTriggerReleased", rightHandTriggerReleased)
rightController.connectSignal("handTriggerIsPressed", rightHandTriggerIsPressed)
rightController.connectSignal("handTriggerChanged", rightHandTriggerChanged)

rightController.setCustomPickingDirection( Pnt3f(0.0,0.0,0.0), Vec3f(0.0,1.0,0.0), Vec3f(1.0, 0.0, 1.0))

setOculusRiftTrackingOriginType(1) # set the origin to standing
setOculusRiftTrackingOrigin( Pnt3f(0.0, 0.0, 0.0))
resetOculusRiftOrientation()
