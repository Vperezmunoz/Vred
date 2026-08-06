# (Deprecated) Change hand color
# source: VR-hands-color.html

# © 2026 Autodesk, Inc. All rights reserved.

def findNodeRecursive(nodeName, node):
    if not node.isValid():
        return None

    if node.getName() == nodeName:
        return node
    
    numChildren = node.getNChildren()
    for i in range(0, numChildren):
        result = findNodeRecursive(nodeName, node.getChild(i))    
        if result:
            return result
        
    return None


def setHandColor(role, color):
    handPrefix = { Hand_Left : "L_", Hand_Right : "R_" }
    print("Hand role:", "left" if role == Hand_Left else "right")
    handMesh = findNodeRecursive(handPrefix[role] + "hand_mesh", getInternalRootNode())
    if handMesh.isValid():
        mat = handMesh.getMaterial()
        # set X-Ray color
        baseColor = vrFieldAccess(mat.fields().getFieldContainer('baseColor'))
        baseColor.setVec3f("color", color[0], color[1], color[2])
    
    hitMesh = findNodeRecursive(handPrefix[role] + "hit_mesh", getInternalRootNode())
    if hitMesh.isValid():
        mat = hitMesh.getMaterial()
        # set Plastic incandescence color
        incandescenceColor = mat.fields().getVec("incandescenceColor", 4)
        mat.fields().setVec4f("incandescenceColor", color[0], color[1], color[2], incandescenceColor[3])
   
# Deprecated class vrOculusTouchController. See vrDeviceService, vrdVRDevice, vrdDeviceInteraction instead.
controller0 = vrOculusTouchController("LeftTouch")
controller1 = vrOculusTouchController("RightTouch")
controller0.setVisible(True)
controller1.setVisible(True)

color = (1.0, 1.0, 1.0)

# Set color when hands are detected in VR mode.
controller0.connectSignal("handRoleChanged", setHandColor, color)
controller1.connectSignal("handRoleChanged", setHandColor, color)

# If the script is executed in VR mode after hands have been detected, force color change:
if controller0.getHandRole() != Hand_Undefined:
    setHandColor(controller0.getHandRole(), color)
if controller1.getHandRole() != Hand_Undefined:
    setHandColor(controller1.getHandRole(), color)

# © 2026 Autodesk, Inc. All rights reserved.

def findNodeRecursive(nodeName, node):
    if not node.isValid():
        return None

    if node.getName() == nodeName:
        return node
    
    numChildren = node.getNChildren()
    for i in range(0, numChildren):
        result = findNodeRecursive(nodeName, node.getChild(i))    
        if result:
            return result
        
    return None


def setHandColor(role, color):
    handPrefix = { Hand_Left : "L_", Hand_Right : "R_" }
    print("Hand role:", "left" if role == Hand_Left else "right")
    handMesh = findNodeRecursive(handPrefix[role] + "hand_mesh", getInternalRootNode())
    if handMesh.isValid():
        mat = handMesh.getMaterial()
        # set X-Ray color
        baseColor = vrFieldAccess(mat.fields().getFieldContainer('baseColor'))
        baseColor.setVec3f("color", color[0], color[1], color[2])
    
    hitMesh = findNodeRecursive(handPrefix[role] + "hit_mesh", getInternalRootNode())
    if hitMesh.isValid():
        mat = hitMesh.getMaterial()
        # set Plastic incandescence color
        incandescenceColor = mat.fields().getVec("incandescenceColor", 4)
        mat.fields().setVec4f("incandescenceColor", color[0], color[1], color[2], incandescenceColor[3])
   
# Deprecated class vrOpenVRController. See vrDeviceService, vrdVRDevice, vrdDeviceInteraction instead.
controller0 = vrOpenVRController("Controller0")
controller1 = vrOpenVRController("Controller1")
controller0.setVisualizationMode(Visualization_Hand)
controller1.setVisualizationMode(Visualization_Hand)

color = (1.0, 1.0, 1.0)

# Set color when hands are detected in VR mode.
controller0.connectSignal("handRoleChanged", setHandColor, color)
controller1.connectSignal("handRoleChanged", setHandColor, color)

# If the script is executed in VR mode after hands have been detected, force color change:
if controller0.getHandRole() != Hand_Undefined:
    setHandColor(controller0.getHandRole(), color)
if controller1.getHandRole() != Hand_Undefined:
    setHandColor(controller1.getHandRole(), color)
