# Rotate
# source: rotate.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to rotate a scene plate
# This example is more complex as simple.py and create.py
# Please study this first
#
# vrSceneplateService is used to create and query a scene plate
# vrdSceneplateNode is used to rotate the scene plate
#

# We introduce this types to make the code more readable
NodeType = vrSceneplateTypes.NodeType
ContentType = vrSceneplateTypes.ContentType
PositionType = vrSceneplateTypes.Position
SizeType = vrSceneplateTypes.SizeType

# Current angle for rotation animation
theAngle = 0.0;

# This function summarizes all necessary steps to create a scene plate and set its properties.
# First we have to create a node using the scene plate service and convert this to an plate.
# Then we set different properties of the new created plate. 
def createPlate(root, image): 
    theNode = vrSceneplateService.createNode(root, NodeType.Frontplate, "plate")
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setContentType(ContentType.Image)
    thePlate.setImage(image) 
    thePlate.setSizeMode(SizeType.Absolute)
    thePlate.setSize(512)
    thePlate.setPosition(PositionType.Center)

# Rotate the plate clockwise
def nextStep():
    global theAngle
    theAngle = theAngle + 0.1
    if theAngle > 360.0:
        theAngle = 0.0

    theNode = vrSceneplateService.findNode("plate");
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setRotation(theAngle)

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Read an image
theDir = vrFileIO.getVREDExamplesDir()
theFile = theDir + "/textures/vred.png"
theFile = theFile.replace('\\', '/');
theImage = vrImageService.loadImage(theFile)

# Create image back plates in the middle of the window
createPlate(theRoot, theImage)

# Start a timer and make each second the next step in this animation
timer = vrTimer(0.1)
timer.connect(nextStep)
timer.setActive(true)
