# Toy Excavator Constraints demo
# source: Toy-Excavator-Constraints.html

# © 2026 Autodesk, Inc. All rights reserved.

# This script is part of the Toy-Excavator-Constraints.vpb and does not run without it.

# Helper class for constraint management. This shows a way how to deal with 
# persistent constraints. Every time we create a new aim or orientation constraint
# we check if this particular constraint is already present in the scene. Otherwise
# we would have identical constraints pile up.

class ConstraintsManager(object):
    def __init__(self):
        pass

    def __compareNodes(self, list1, list2):
        if len(list1) != len(list2):
            return False
        for i in range(len(list1)):
            if list1[i].getObjectId() != list2[i].getObjectId():
                return False
        return True

    def __hasAimConstraint(self, targetNodes, upTargetNodes, constrainedNode):
        existingConstraints = vrConstraintService.findConstrainedNode(constrainedNode)
        for c in existingConstraints:
            if isinstance(c, vrdAimConstraintNode):
                return (self.__compareNodes(c.getTargetNodes(), targetNodes) and 
                    self.__compareNodes(c.getUpVectorTargetNodes(), upTargetNodes))
        return False

    def __hasOrientationConstraint(self, targetNodes, constrainedNode):
        existingConstraints = vrConstraintService.findConstrainedNode(constrainedNode)
        for c in existingConstraints:
            if isinstance(c, vrdOrientationConstraintNode):
                return self.__compareNodes(c.getTargetNodes(), targetNodes)
        return False

    def addAimConstraint(self, targetNodes, upTargetNodes, constrainedNode):
        if not self.__hasAimConstraint(targetNodes, upTargetNodes, constrainedNode):
            vrConstraintService.createAimConstraint(targetNodes, upTargetNodes, constrainedNode)
        else:
            print ("aim constraint already exists!")

    def addOrientationConstraint(self, targetNodes, constrainedNode):
        if not self.__hasOrientationConstraint(targetNodes, constrainedNode):
            vrConstraintService.createOrientationConstraint(targetNodes, constrainedNode)
            constraint = vrConstraintService.createOrientationConstraint(targetNodes, constrainedNode)            
            constrainedObject = constraint.getConstrainedObject(constrainedNode)
            constrainedObject.setUseWorldSpaceTargetSystem(True)
            constrainedObject.setUseWorldSpaceConstrainedSystem(True)
            constrainedObject.setMaintainOffset(False)
        else:
            print ("orientation constraint already exists!")


# This function is not used in the demo, but can be called to delete all constraints
# again. It only runs on a subtree so that it does not remove any aim cameras by accident. 
# call: deleteAllConstraintsInSubtree(vrNodeService.findNode("Toy Digger Assembly"))
def deleteAllConstraintsInSubtree(root):
    numChildren = root.getChildCount()
    for i in range(numChildren):
        deleteAllConstraintsInSubtree(root.getChild(i))

    constraints = vrConstraintService.findConstrainedNode(root)
    if (len(constraints)) > 0:
        for c in constraints:
            vrConstraintService.deleteConstraint(c)


constraints = ConstraintsManager()

armLong = vrNodeService.findNode("Arm Long")
armLongHandle = vrNodeService.findNode("Arm Long Handle")
armShort = vrNodeService.findNode("Arm Short")
armShortHandle = vrNodeService.findNode("Arm Short Handle")
constraints.addOrientationConstraint([armLongHandle], armLong)
constraints.addOrientationConstraint([armShortHandle], armShort)

cyl1LeftHullTarget = vrNodeService.findNode("Zylinder 1 Left Hull Target")
cyl1LeftStickTrans = vrNodeService.findNode("Zylinder 1 Left Stick Trans")
cyl1LeftHullTrans = vrNodeService.findNode("Zylinder 1 Left Hull Trans")
cap1Body = vrNodeService.findNode("Cap 1 Body")
constraints.addAimConstraint([cyl1LeftHullTarget], [cap1Body], cyl1LeftStickTrans)
constraints.addOrientationConstraint([cyl1LeftStickTrans], cyl1LeftHullTrans)

cyl1RightHullTarget = vrNodeService.findNode("Zylinder 1 Right Hull Target")
cyl1RightStickTrans = vrNodeService.findNode("Zylinder 1 Right Stick Trans")
cyl1RightHullTrans = vrNodeService.findNode("Zylinder 1 Right Hull Trans")
cap2Body = vrNodeService.findNode("Cap 2 Body")
constraints.addAimConstraint([cyl1RightHullTarget], [cap2Body], cyl1RightStickTrans)
constraints.addOrientationConstraint([cyl1RightStickTrans], cyl1RightHullTrans)

cyl2HullTarget = vrNodeService.findNode("Zylinder 2 Hull Target")
cyl2StickTrans = vrNodeService.findNode("Zylinder 2 Stick Trans")
cyl2HullTrans = vrNodeService.findNode("Zylinder 2 Hull Trans")
constraints.addAimConstraint([cyl2HullTarget], [], cyl2StickTrans)
constraints.addOrientationConstraint([cyl2StickTrans], cyl2HullTrans)
