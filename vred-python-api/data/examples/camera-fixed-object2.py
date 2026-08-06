# Camera fixed object 2
# source: camera-fixed-object2.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing demo script!")

newScene()

# define class that calls a render update every frame
class CameraUpdate(vrAEBase):
    def __init__(self, camera_node, camera_transform):
        vrAEBase.__init__(self)
        self.camera_node = camera_node
        self.camera_transform = camera_transform
        self.addLoop()
    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
    def loop(self):
        if self.isActive():
            camera_matrix = self.camera_node.getWorldTransform()
            self.camera_transform.setTransformMatrix(camera_matrix, false)

loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
updateScene()
calcVertexNormals()
enableHeadlight(true)
ignoreAutoHeadlight()

obj = findNode("Teddy_Bear");
obj.makeTransform()
obj.setTranslation(0, 0, -200)

camera_transform = createNode("Transform", "CameraTransform")
obj.getParent().addChild(camera_transform)
camera_transform.addChild(obj)

camera_update = CameraUpdate(getCamNode(0), camera_transform)
camera_update.setActive(true)
