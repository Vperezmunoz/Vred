# Repeat
# source: repeat.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to insert one back plate
# This plate will cover the whole window
#
# vrSceneplateService is used to create new scene plates
# vrdSceneplateNode is used to change scene plate properties
#

# We introduce this types to make the code more readable
NodeType = vrSceneplateTypes.NodeType
ContentType = vrSceneplateTypes.ContentType
SizeType = vrSceneplateTypes.SizeType
RepeatType = vrSceneplateTypes.RepeatMode

# This function summarizes all necessary steps to create a scene plate and set its properties.
# First we have to create a node using the scene plate service and convert this to an plate.
# Then we set different properties of the new created plate. 
def createPlate(root, image): 
    theNode = vrSceneplateService.createNode(root, NodeType.Backplate, "plate")
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setContentType(ContentType.Image)
    thePlate.setImage(image) 
    thePlate.setSizeMode(SizeType.Absolute)
    thePlate.setSize(512)
    thePlate.setRepeatMode(RepeatType.Repeat)

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

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Read an image
theImage = createVREDImage()

# Create image plate repeat all over the window
createPlate(theRoot, theImage)
