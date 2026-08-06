# Fade
# source: fade.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to change scene plate's transparency
# This example is more complex as simple.py and create.py
# Please study this first
#
# vrSceneplateService is used to create and query a scene plate
# vrdSceneplateNode is used to change scene plate's transpacency
#

# We introduce this types to make the code more readable
NodeType = vrSceneplateTypes.NodeType
ContentType = vrSceneplateTypes.ContentType
PositionType = vrSceneplateTypes.Position
SizeType = vrSceneplateTypes.SizeType

# Values used for fade animation
theStep = 0.01;
theTransparency = 0.0;

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

# Load an image
# Get the example directory
# Dive in to the texture directory
# Make path windows like with back slashes
# Load image with help of image service
def createVREDImage():
    theDir = vrFileIO.getVREDExamplesDir()
    theFile = theDir + "/textures/vred.png"
    theFile = theFile.replace('\\', '/');
    theImage = vrImageService.loadImage(theFile)
    return theImage

# Fade in and out the plate
def nextStep():
    global theStep
    global theTransparency
    theTransparency = theTransparency + theStep

    if theTransparency >= 1.0:
        theStep = -0.01

    if theTransparency <= 0.0:
        theStep = 0.01

    theNode = vrSceneplateService.findNode("plate");
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setTransparency(theTransparency)

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Read an image
theImage = createVREDImage()

# Create image plate in the middle of the window
createPlate(theRoot, theImage)

# Start a timer and make each second the next step in this animation
timer = vrTimer(0.1)
timer.connect(nextStep)
timer.setActive(true)
