# Camera fixed object 1
# source: camera-fixed-object1.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing demo script!")

newScene()

# All objects that are attached to the camera (fixed objects)
# need to be removed by the script. We define a special python
# function to clean up and tell vred to call this function when 
# newScene is called or the users presses the new button in vred
def newSceneCallback():
    # remove object from camera.
    camera_node.subChild(obj)

setNewSceneCB(newSceneCallback)

loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
updateScene()
calcVertexNormals()
enableHeadlight(true)
ignoreAutoHeadlight()

obj = findNode("Teddy_Bear");
obj.makeTransform()
obj.setTranslation(0, 0, -200)

camera_node = getCamNode(0)

camera_node.addChild(obj)
