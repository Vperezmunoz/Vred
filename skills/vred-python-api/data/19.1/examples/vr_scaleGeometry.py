# Scale geometry in VR by using controllers
# source: scaleGeometry.html

# © 2026 Autodesk, Inc. All rights reserved.

class GeometryScaler:
    def __init__(self):
        
        # Init all the class variables
        # Two devices are needed. The major device is the one that starts the whole scaling procedure and selects the object
        self.majorDevice = vrdVRDevice()        
        self.secondaryDevice = vrdVRDevice()
        # Flags that indicate the current state
        self.objectSelected = False        
        self.isSelecting = False
        self.isScaling = False
        # Picked node
        self.hitNode = vrdNode()
        # Hitpoints of the controller rays
        self.hitPoint1 = PySide6.QtGui.QVector3D(0.0, 0.0, 0.0)
        self.hitPoint2 = PySide6.QtGui.QVector3D(0.0, 0.0, 0.0)
        # Distance of hitpoints, when the scaling starts
        self.initialDistance = 0.0

        # Get the default pointer actions ...
        pointer = vrDeviceService.getInteraction("Pointer")
        self.startSelectionAction = pointer.getControllerAction("prepare")
        self.selectAction = pointer.getControllerAction("start")
        self.unselectAction = pointer.getControllerAction("execute")
        self.stopSelectionAction = pointer.getControllerAction("abort")
        # ... and connect the corresponding methods
        self.startSelectionAction.signal().triggered.connect(self.startSelection)
        self.selectAction.signal().triggered.connect(self.selectElement)
        self.unselectAction.signal().triggered.connect(self.unselectElement)
        self.stopSelectionAction.signal().triggered.connect(self.stopSelection)        

        # Get the controllers for easy access
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")


    def startSelection(self, action, device):
        # Check if the state and device is correct        
        if self.objectSelected or self.isSelecting or self.isSecondaryDevice(device):
            return

        # Update which device is major and secondary device
        self.updateDevices(device.getName())
        # Set current state
        self.isSelecting = True        

    def selectElement(self, action, device):
        # If the major device selects a node it is marked for scaling,
        # if the secondary device selects a node, it actually starts the scaling.
        if self.isMajorDevice(device):
            self.markNodeForScaling(device)                    
        elif self.isSecondaryDevice(device):
            self.startScaling(device)        

    def markNodeForScaling(self, device):
        # Check if the state is correct
        if not self.isSelecting:
            return

        # Intersect the pick ray with the scene
        intersection = device.pick()
        if not intersection.hasHit():
            return

        # Assign what actually has been intersected
        self.hitNode = intersection.getNode()
        self.hitPoint1 = intersection.getPoint()        
        self.isSelecting = False
        self.objectSelected = True

        # Activate the ray on the secondary device, which is needed for scaling
        self.secondaryDevice.enableRay("controllerhandle")        

    def startScaling(self, device):
        # Check if the state is correct                
        if not self.objectSelected:
            return

        # Intersect the pick ray of the secondary device with the scene
        intersection = self.secondaryDevice.pick()
        if not intersection.hasHit():
            return
        
        # Check if both rays intersect with the same node
        node = intersection.getNode()
        if node.getObjectId() != self.hitNode.getObjectId():
            return

        # Get the hintpoint and calculate the initial distance
        self.hitPoint2 = intersection.getPoint()
        self.initialDistance = self.hitPoint1.distanceToPoint(self.hitPoint2)
        # Get the current scale of the node
        self.initialScale = getTransformNodeScale(self.hitNode)
        
        # Connect the actual scaling method here
        self.majorDevice.signal().moved.connect(self.scale)        

    def unselectElement(self, action, device):
        # Reset everything        
        self.stopScaling()
        self.objectSelected = False
        self.hitNode = vrdNode()
        self.secondaryDevice.disableRay()        

    def stopScaling(self):    
        # Check the state    
        if not self.isScaling:
            return

        # Disconnect after scaling    
        self.majorDevice.signal().moved.disconnect(self.scale)  
        # Update the state
        self.isScaling = False                     

    def stopSelection(self, action, device):                
        if not self.isMajorDevice(device):
            return

        # Update the state
        self.isSelecting = False
        # Reset devices
        self.majorDevice = vrdVRDevice()
        self.secondaryDevice = vrdVRDevice()                

    def isMajorDevice(self, device):                
        return device.getName() == self.majorDevice.getName()

    def isSecondaryDevice(self, device):
        return device.getName() == self.secondaryDevice.getName()

    def updateDevices(self, majorName):
        # Update by name, which device is the major device and which is secondary
        if majorName == self.leftController.getName():
            self.majorDevice = self.leftController
            self.secondaryDevice = self.rightController
        else:
            self.majorDevice = self.rightController
            self.secondaryDevice = self.leftController            

    def scale(self, device):
        intersection1 = self.majorDevice.pick()
        intersection2 = self.secondaryDevice.pick()

        self.hitPoint1 = intersection1.getPoint()
        self.hitPoint2 = intersection2.getPoint()

        nodeId1 = intersection1.getNode().getObjectId()
        nodeId2 = intersection2.getNode().getObjectId()        

        # Check if both rays intersect with the same node
        if nodeId1 != self.hitNode.getObjectId() or nodeId2 != self.hitNode.getObjectId():
            self.majorDevice.signal().moved.disconnect(self.scale)
            self.isScaling = False
            return

        # Update state
        self.isScaling = True
        
        # Calculate the scale factor depending on the distance of the two hitpoints
        distance = self.hitPoint1.distanceToPoint(self.hitPoint2)
        scaleFactor = max(min(distance / self.initialDistance, 5.0), 0.2)
        scaleX = scaleFactor * self.initialScale.x()
        scaleY = scaleFactor * self.initialScale.y()
        scaleZ = scaleFactor * self.initialScale.z()

        # Scale node        
        setTransformNodeScale(self.hitNode, scaleX, scaleY, scaleZ)        

scaler = GeometryScaler()
