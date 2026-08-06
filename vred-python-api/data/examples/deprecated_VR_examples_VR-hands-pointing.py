# (Deprecated) Touch objects in pointing pose
# source: VR-hands-pointing.html

lastHitNodes = {}

def controllerMoved(controller, hitViz):
    hitViz.setActive(False)
    if controller.isHandPoseActive(Pose_Pointing):
        hit = controller.pickNodeWithFinger(Finger_Index)
        hitNode = hit[0]
        hitPoint = hit[1]
        if hitNode.isValid():
            hitViz.setTranslation(hitPoint.x(), hitPoint.y(), hitPoint.z())
            hitViz.setActive(True)
            global lastHitNodes
            if not controller in lastHitNodes or lastHitNodes[controller].getID() != hitNode.getID():
                hitNormal = hit[2]
                hitUV = hit[3]
                button = 1
                callAllPickingPressed(hitNode, hitPoint, hitNormal, hitUV, button)
                callAllPickingReleased(hitNode, hitPoint, hitNormal, hitUV, button)
                lastHitNodes[controller] = hitNode


def handPoseStopped(poseId, controller):
    if poseId == Pose_Pointing:
        global lastHitNodes
        if controller in lastHitNodes:
            del lastHitNodes[controller]

# Deprecated class vrOpenVRController. See vrDeviceService, vrdVRDevice, vrdDeviceInteraction instead.
controller0 = vrOpenVRController("Controller0")
controller1 = vrOpenVRController("Controller1")
controller0.setVisualizationMode(Visualization_Hand)
controller1.setVisualizationMode(Visualization_Hand)

hitViz0 = findNode("HitViz0")
hitViz1 = findNode("HitViz1")

controller0.connectSignal("controllerMoved", controllerMoved, controller0, hitViz0)
controller0.connectSignal("handPoseStopped", handPoseStopped, controller0)

controller1.connectSignal("controllerMoved", controllerMoved, controller1, hitViz1)
controller1.connectSignal("handPoseStopped", handPoseStopped, controller1)
