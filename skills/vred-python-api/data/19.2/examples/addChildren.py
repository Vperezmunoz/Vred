# Add child nodes
# source: addChildren.html

# © 2026 Autodesk, Inc. All rights reserved.

# clean the scene
newScene()

# This example creates nodes and adds them as children to a 
# parent node with API v2.
#
# Please note, the create functions have a parent parameter that lets
# you specify the target parent directly but for demonstration purposes
# the nodes are created under root and then reparented in this script.

root = vrScenegraphService.getRootNode()

# create planet and moons
planetNode = vrGeometryService.createSphere(root, 3.0, 32, 32, QColor.fromRgbF(0.0, 0.1, 0.6))
planetNode.setName("Planet")

moonColor = QColor.fromRgbF(0.0, 0.0, 0.0)
moon1Node = vrGeometryService.createSphere(root, 0.5, 16, 16, moonColor)
moon1Node.setName("Moon")
moon1Node.setTranslation(QVector3D(5.0,3.0,5.0))

moon2Node = vrGeometryService.createSphere(root, 0.2, 16, 16, moonColor)
moon2Node.setName("Moon2")
moon2Node.setTranslation(QVector3D(-1.0,6.0,0.0))

# create a list of the moon nodes
moonlist = []
moonlist.append(moon1Node)
moonlist.append(moon2Node)

# create a new group for the moons
moonGroup = vrScenegraphService.createNode(vrScenegraphTypes.TransformNode, root, "Moons")

# add moons as children to the group
moonGroup.children.append(moonlist)

# create a new group for the planet and the moon group
planetGroup = vrScenegraphService.createNode(vrScenegraphTypes.TransformNode, root, "Planet") 

# add the planet and the moon group to the planet group
planetGroup.children.append([moonGroup, planetNode])

# moving the planet group with all children
planetGroup.setTranslation(QVector3D(5.0,5.0,0.0))

# hide the environment
environment = vrMaterialService.findMaterial("Studio")
environment.setVisible(False)
environment.setShadowPlaneVisible(False)
