# Simple
# source: simple.html

# © 2026 Autodesk, Inc. All rights reserved.
#
# Example to show how to insert one front plate
#
# vrSceneplateService is used to create new scene plates
# vrdSceneplateNode is used to change scene plate properties
#

# Query parent object for all scene plate creation
theRoot = vrSceneplateService.getRootNode()

# Create text front plates attached to windows sides
theNode = vrSceneplateService.createNode(theRoot, vrSceneplateTypes.Frontplate, "Plate")

# Cast it to a scene plate object
thePlate = vrdSceneplateNode(theNode)

# Set scene plate type
thePlate.setContentType(vrSceneplateTypes.Text)

# Set some properties from scene plate 
thePlate.setText("The Plate")
theFontColor = QVector3D(0.0, 0.2, 1.0)
thePlate.setFontColor(theFontColor)
thePlate.setPosition(vrSceneplateTypes.Center)
