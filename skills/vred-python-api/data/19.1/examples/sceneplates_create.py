# Create
# source: create.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to insert front plates
#
# vrSceneplateService is used to create new scene plates
# vrdSceneplateNode is used to change scene plate properties
#

# We introduce this types to make the code more readable
NodeType = vrSceneplateTypes.NodeType
ContentType = vrSceneplateTypes.ContentType
PositionType = vrSceneplateTypes.Position

# This function summarizes all necessary steps to create a scene plate and set its properties.
# First we have to create a node using the scene plate service and convert this to an plate.
# Then we set different properties of the new created plate. 
def createPlate(root, name, position):
    theNode = vrSceneplateService.createNode(root, NodeType.Frontplate, name)
    thePlate = vrdSceneplateNode(theNode)
    thePlate.setContentType(ContentType.Text)
    thePlate.setText(name)
    theFontColor = QVector3D(0.0, 0.2, 1.0)
    thePlate.setFontColor(theFontColor)
    thePlate.setPosition(position)

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Create text front plates attached to windows sides
createPlate(theRoot, "0", PositionType.Center)
createPlate(theRoot, "1", PositionType.TopLeft)
createPlate(theRoot, "2", PositionType.Top)
createPlate(theRoot, "3", PositionType.TopRight)
createPlate(theRoot, "4", PositionType.Right)
createPlate(theRoot, "5", PositionType.BottomRight)
createPlate(theRoot, "6", PositionType.Bottom)
createPlate(theRoot, "7", PositionType.BottomLeft)
createPlate(theRoot, "8", PositionType.Left)
