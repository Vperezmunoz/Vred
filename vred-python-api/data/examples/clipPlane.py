# Creating a local clipping plane
# source: clipPlane.html

# © 2026 Autodesk, Inc. All rights reserved.

# This example creates a clipped sphere geometry with API v2.
# Shortcut to toggle the clipping plane on and off is key C.

# Create sphere and move it up
root = vrScenegraphService.getRootNode()
sphere = vrGeometryService.createSphere(root, 500, 32, 32, QColor.fromRgbF(1.0, 1.0, 1.0))
sphere.setTranslation(QVector3D(0 ,0 ,500))

# Create local clip plane
clipPlane = vrScenegraphService.createNode(vrScenegraphTypes.ClipPlaneNode, root)
# The transformation of the clip plane node only changes the transformation 
# of the plane but does not transform its children
clipPlane.setTranslation(QVector3D(0, 0, 500))

# Add sphere as child of clip plane. All children are clipped by the plane.
clippedObjects = [sphere]
clipPlane.children.append(clippedObjects)

# Function to activate and deactivate the clip plane
def toggleClipPlane():
    if clipPlane.isValid():
        clipPlane.setEnabled(not clipPlane.getEnabled())

# Connect toggle to key 'c'
keyC = vrKey(Key_C)
keyC.connect(toggleClipPlane)

print("Press key 'c' to toggle the clip plane.")
