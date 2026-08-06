# turntable demo
# source: turntable.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing turntable script!")

# Everything behind # is a comment!

newScene()

loadGeometry("$VRED_EXAMPLES/geo/turntable.osb")
updateScene()

# Searches for the node with the name "podest"
turntable = findNode("turntable");
turntable.makeTransform()
center = turntable.getCenter();

# create interpolator for rotation
turntableInt = vrInterpolator()

# This rotates about the z-axis from angle (0, 0, 0) to (0, 0, 359) in 8 seconds.
#turntableSlide = vrRotationSlide(turntable, 0, 0, 0, 0, 0, 359, 8.0)

# You can also define a rotation axis via 2 points.
# we use the center of the object.
turntableSlide = vrRotationAxisSlide(turntable, center[0], center[1], center[2],   center[0], center[1] , center[2] + 1.0,  0, 359, 8.0)
turntableInt.add(turntableSlide)

# define key r to toggle rotation of the turntable
keyR = vrKey(Key_R)
keyR.connect(turntableInt, SWITCH_TOGGLE)
vrLogWarning("Press r to rotate.")
