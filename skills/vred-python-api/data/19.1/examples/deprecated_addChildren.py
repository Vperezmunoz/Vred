# (Deprecated) Add child nodes
# source: addChildren.html

# © 2026 Autodesk, Inc. All rights reserved.

# clean the scene
newScene();

# create planet and moons
planetNode = createSphere(4, 3.0, .0 , .0, .0)
planetNode.setName("Planet")

moon1Node = createSphere(4, .5, .0 , .0, .0)
moon1Node.setName("Moon")
moon1Node.setTranslation(5.0,3.0,5.0)

moon2Node = createSphere(4, .2, .0 , .0, .0)
moon2Node.setName("Moon2")
moon2Node.setTranslation(-1.0,6.0,0.0)

# create a list of the moon nodes
moonlist = []
moonlist.append(moon1Node)
moonlist.append(moon2Node)

# create a new group for the moons
moonGroup = createNode("Group","Moons")

# add moons as children to the group
addChilds(moonGroup,moonlist)

# create a new group for the planet and the moon group
planetGroup = createNode("Group","Planet")

# add the planet and the moon group to the planet group
addChilds(planetGroup, [moonGroup, planetNode])

# moving the planet group with all children
planetGroup.setTranslation(5.0,5.0,0.0)
