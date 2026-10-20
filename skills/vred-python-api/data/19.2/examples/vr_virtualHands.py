# Virtual VR controllers
# source: virtualHands.html

# © 2026 Autodesk, Inc. All rights reserved.

from PySide6 import QtGui

menuButton = vrKey(Key_M)
touchpadButton = vrKey(Key_T)
pressButton = vrKey(Key_P)
    
class VirtualHands(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.createHandles()
        # create right hand
        self.rightHand = vrDeviceService.createVRDevice("right-controller")
        # create left hand
        self.leftHand = vrDeviceService.createVRDevice("left-controller")
        # simulate keys
        self.touched = False
        self.pressed = False
        menuButton.connect(self.toggleMenu,SWITCH_TOGGLE)
        touchpadButton.connect(self.toggleTouched,SWITCH_TOGGLE)
        pressButton.connect(self.togglePressed,SWITCH_ON)
        self.addLoop()
    def loop(self):
        # Use the sphere transformations as tracking values
        leftPos = self.leftTrans.getWorldTransform()
        leftPos.translate(40,-90,-200)
        rightPos = self.rightTrans.getWorldTransform()
        rightPos.translate(-40,-90,-200)
        self.rightHand.setTrackingMatrix(rightPos)
        self.leftHand.setTrackingMatrix(leftPos)
    def toggleMenu(self,value):
        self.leftHand.setButtonPressed(True,"menu")
        self.leftHand.setButtonPressed(False,"menu")
    def toggleTouched(self,value):
        self.touched = not self.touched
        self.rightHand.setButtonTouched(self.touched,"trigger")
    def togglePressed(self,value):
        self.rightHand.setButtonPressed(True,"trigger")
        self.rightHand.setButtonPressed(False,"trigger")
    def createHandles(self):
        # create two spheres that can be used to
        # transform the hands
        node = findNode("RightHandle")
        if node.isValid():
            deleteNode(node)
        self.rightTrans = createSphere(3, 30, .7, .7, 1)
        self.rightTrans.setName("RightHandle")
        setTransformNodeTranslation(self.rightTrans,-280,90,200,True)
        setTransformNodeRotation(self.rightTrans,0,180,0)
        self.rightTrans = vrNodeService.getNodeFromId(self.rightTrans.getID())
        node = findNode("LeftHandle")
        if node.isValid():
            deleteNode(node)
        self.leftTrans = createSphere(3, 30, .7, .7, 1)
        self.leftTrans.setName("LeftHandle")
        setTransformNodeTranslation(self.leftTrans,280,90,200,True)
        setTransformNodeRotation(self.leftTrans,0,180,0)
        self.leftTrans = vrNodeService.getNodeFromId(self.leftTrans.getID())

hands = VirtualHands()

print("Use key M to open the VR Menu")
print("Use T to simulate trigger touched")
print("Use P to simulate trigger pressed")
