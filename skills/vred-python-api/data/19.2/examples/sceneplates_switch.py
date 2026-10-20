# Switch
# source: switch.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to query front plates
# This example is more complex as simple.py and create.py
# Please study this first
#
# vrSceneplateService is used to query scene plates and set defaults
# vrdSceneplateNode is used to change scene plate properties
#

# We introduce this types to make the code more readable
NodeType = vrSceneplateTypes.NodeType
ContentType = vrSceneplateTypes.ContentType
PositionType = vrSceneplateTypes.Position

# An array with all node names. We use this for scene plate creation and query.
theNodeNames = ["1", "2", "3", "4", "5", "6", "7", "8"]

# The curent shown plate
thePlate = -1

# This function summarizes all necessary steps to create a scene plate and set its properties.
# First we have to create a node using the scene plate service and convert this to an plate.
# Then we set different properties of the new created plate. 
def createPlate(root, index, position):
    global theNodeNames
    global theFontColor
    theName = theNodeNames[index]
    theNode = vrSceneplateService.createNode(root, NodeType.Frontplate, theName)
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setContentType(ContentType.Text)
    thePlate.setText(theName) 
    thePlate.setPosition(position)

# This function creates all used front plates
def propagateScene(root): 
    global theSwitch

    createPlate(root, 0, PositionType.TopLeft)
    createPlate(root, 1, PositionType.Top)
    createPlate(root, 2, PositionType.TopRight)
    createPlate(root, 3, PositionType.Right)
    createPlate(root, 4, PositionType.BottomRight)
    createPlate(root, 5, PositionType.Bottom)
    createPlate(root, 6, PositionType.BottomLeft)
    createPlate(root, 7, PositionType.Left)

    thePlates = vrSceneplateService.getAllSceneplates()
    theSwitch = vrSceneplateService.createSwitchForNodes(thePlates)

# Step to the next plate
def nextStep():
    global thePlate
    global theSwitch
    global theNodeNames

    thePlate = thePlate + 1
    if thePlate >= len(theNodeNames):
        thePlate = 0

    theSwitch.setChoice(thePlate)

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Set defaults colors
vrSceneplateService.setDefaultBackgroundTransparency(1.0)
vrSceneplateService.setDefaultBackgroundColor(QVector3D(0.6, 0.6, 0.6))
vrSceneplateService.setDefaultFontColor(QVector3D(0, 0.5, 0.5))

# Create text front plates attached to windows sides
propagateScene(theRoot)

# Start a timer and make each second the next step in this animation
timer = vrTimer(1.0)
timer.connect(nextStep)
timer.setActive(true)
