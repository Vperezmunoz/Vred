# Find nodes and materials
# source: find.html

# © 2026 Autodesk, Inc. All rights reserved.

# demo script to show how to search nodes and materials
print("Executing find script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
updateScene()

# find all nodes via regular expression.
nodes = findNodes("Eye_*", true)

# search material
brown = findMaterial("fur_brown")

# set the material of all found nodes to be brown
for geo in nodes:
    geo.setMaterial(brown)


# search material
white = findMaterial("fur_white")

# find nodes via a list of names. If you don't like to type all the names
# just select the nodes in the scenegraph press ctrl-c and ctrl-v in the editor.
nodes = findNodes(["Tail", "Nose"])

# set the material of all found nodes to be white
for geo in nodes:
    geo.setMaterial(white)
