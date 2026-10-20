# (Deprecated) openvr_tracker_setup
# source: openvr_tracker_setup.html

# © 2026 Autodesk, Inc. All rights reserved.

# Deprecated. See vr/attachToTracker.py instead.
def tracker0Moved():
    # Apply tracking matrix of the tracker to a Matrix Transform node
    # named "MatrixTracker0" in the Scenegraph.
    trackerNode = findNode("MatrixTracker0") 
    trackerNode.setTransformMatrix( tracker0.getWorldMatrix(), false)

# Identify trackers with "GenericTracker0", "GenericTracker1", and so on.
tracker0 = vrOpenVRController("GenericTracker0")
tracker0.connectSignal("controllerMoved", tracker0Moved)
