# (Deprecated) Creating a local clipping plane
# source: clipPlane.html

# © 2026 Autodesk, Inc. All rights reserved.

# Create sphere and move it up
sphere = createSphere(3, 500, 1, 1,1)
setTransformNodeTranslation(sphere, 0,0,500, true)

# Create local clip plane
nodeType = "ClipPlane"
clipPlane = createNode(nodeType)
setTransformNodeTranslation(clipPlane, 0,0,500, true)

# Add sphere as child of clip plane. All children are clipped by the plane.
clippedObjects = [sphere]
addChilds(clipPlane, clippedObjects)

# Function to activate and deactivate the clip plane
def toggleClipPlane():
    if clipPlane.isValid():
        # The clip plane's boolean field "on" stores whether clipping is enabled.
        # Use vrFieldAccess to get and set the current state.
        isLocalClipPlaneEnabled = clipPlane.fields().getBool("on")
        clipPlane.fields().setBool("on", not isLocalClipPlaneEnabled)

# Connect toggle to key 'c'
keyC = vrKey(Key_C)
keyC.connect(toggleClipPlane)

print("Press key 'c' to toggle the clip plane.")
