# Simple constraints demo
# source: SimpleConstraints.html

sphere = vrNodeService.findNode("Sphere")
sphere1 = vrNodeService.findNode("Sphere1")
box = vrNodeService.findNode("Box")
cone = vrNodeService.findNode("Cone")
torus = vrNodeService.findNode("Torus")

created = False
global c1, c2, c3, c4

def createSimpleConstraints():
    global c1, c2, c3, c4, created
    # Box position will be synchronized with average of both spheres w/o keeping any offset
    c1 = vrConstraintService.createPositionConstraint([sphere, sphere1], box, False)
    # Cone position will be synchronized with red sphere one and keeps its offset
    c2 = vrConstraintService.createPositionConstraint([sphere], cone, True)
    # Furthermore will the cone point towards the torus
    c3 = vrConstraintService.createAimConstraint([torus], [], cone)
    # Furthermore the box will get the orientation of the cone
    c4 = vrConstraintService.createOrientationConstraint([cone], box)
    # Hide the info scene plates
    infoNode = vrSceneplateService.findNode("Info")
    infoNode.setVisibilityFlag(False)
    created = True

def deleteSimpleConstraints():
    global created
    all = vrConstraintService.getConstraints()
    for c in all:
        vrConstraintService.deleteConstraint(c)
    created = False

def changeConeTarget():
    global c3
    if not created:
        return
    # The cone will now be influenced by the yellow sphere instead of the torus
    c3.setTargetNodes([sphere1])

def changeYellowSphereWeight(weight):
    global c1
    if not created:
        return
    # Change the weight of the yellow sphere for the constraint with the box target
    c1.setTargetNodeWeight(sphere1, weight)
