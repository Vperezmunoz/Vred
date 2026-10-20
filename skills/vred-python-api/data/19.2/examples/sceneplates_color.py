# Color
# source: color.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to rotate a scene plate
# This example is more complex as simple.py and create.py
# Please study this first
#
# vrSceneplateService is used to create and query a scene plate
# vrdSceneplateNode is used to change scene plate's HSB color
#

# We introduce this types to make the code more readable
NodeType = vrSceneplateTypes.NodeType
ContentType = vrSceneplateTypes.ContentType
PositionType = vrSceneplateTypes.Position
SizeType = vrSceneplateTypes.SizeType

# Current values for color animation
theHue = 0.0;
theContrast = 1.0;
theBrightness = 1.0;
theSaturation = 1.0;

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

# Color correction for the plate
def nextStep():
    global theHue
    global theContrast
    global theBrightness
    global theSaturation

    theHue = theHue + 1.5
    theContrast = theContrast + 0.01
    theBrightness = theBrightness + 0.02
    theSaturation = theSaturation + 0.03

    if theHue > 360.0:
        theHue = 0.0

    if theContrast > 2.0:
        theContrast = 0.0

    if theBrightness > 2.0:
        theBrightness = 0.0
    
    if theSaturation > 2.0:
        theSaturation = 0.0

    theNode = vrSceneplateService.findNode("plate");
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setHueShift(theHue)
    thePlate.setContrast(theContrast)
    thePlate.setBrightness(theBrightness)
    thePlate.setSaturation(theSaturation)

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
