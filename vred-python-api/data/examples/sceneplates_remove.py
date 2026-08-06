# Remove
# source: remove.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to create, query and remove scene plates
# This example is more complex as simple.py and create.py
# Please study this first
#
# vrSceneplateService is used to create, query and remove scene plates
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
    thePlate.setFontColor(QVector3D(0.0, 0.5, 0.5))
    thePlate.setPosition(position)

# This function creates all used front plates
def propagateScene(root):    
    createPlate(root, "1", PositionType.TopLeft)
    createPlate(root, "2", PositionType.Top)
    createPlate(root, "3", PositionType.TopRight)
    createPlate(root, "4", PositionType.Right)
    createPlate(root, "5", PositionType.BottomRight)
    createPlate(root, "6", PositionType.Bottom)
    createPlate(root, "7", PositionType.BottomLeft)
    createPlate(root, "8", PositionType.Left)

# Query all scene plates
# If no plates exists, create new plates
# If plates exists remove all 
def togglePlates():
   thePlates = vrSceneplateService.getAllSceneplates()
   if len(thePlates) > 0:
       vrSceneplateService.removeNodes(thePlates)
   else:
       root = vrSceneplateService.getRootNode()
       propagateScene(root)

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Create text front plates attached to windows sides
propagateScene(theRoot)

# Define key R to remove or to create all scene plates
keyR = vrKey(Key_D)
keyR.connect(togglePlates)

# Write instruction on console
vrLogInfo("Press key 'd' to remove or create scene plates")
