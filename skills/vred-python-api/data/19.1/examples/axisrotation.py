# Axis rotation example
# source: axisrotation.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing axisrotation script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/axis_rotation.osb")
updateScene()
calcVertexNormals()

# For the axis rotation we need a new
# transformation node we can't use the
# already existing "cube" transformation node!
# Well "Box" is not a unique name so we
# search via path.
# We also use wildcards for matching the long
# group names in the root.
cube = findNodePath("*/*/A/Box", True);
cube.makeTransform()

axis = findNode("Box_Axis");

# define rotation of cube around axis from 0 to 359 degrees in 8 seconds
cubeInt = vrInterpolator()
cubeSlide = vrRotationAxisSlide(cube, axis, 0, 359, 8.0)
cubeInt.add(cubeSlide)
cubeInt.setActive(true)

print("cube is rotating around its center")
