# Collision Example 1
# source: collision1.html

# © 2026 Autodesk, Inc. All rights reserved.

# Collision demo

newScene()

####################
# create 3 objects #
####################
obja = createBox(2, 2, 2, 1, 1, 1, 1, 0, 0, 0)
obja.makeTransform()
obja.setTranslation(-5, 0, 0)

objb = loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
objb.makeTransform()
objb.setScale(0.01, 0.01, 0.01)
objb.setTranslation(0, 0, 0)

objc = createBox(2, 2, 2, 1, 1, 1, 0, 0, 1, 0)
objc.makeTransform()
objc.setTranslation(5, 0, 0)

updateScene()


########################################################################
# find Teddy_Bear node and rotate around axis 360 degrees in 8 seconds #
########################################################################
head = findNode("Teddy_Bear")

# create a rotation axis and hide it (only needed)
# to pass to vrRotationAxisSlide command
axis = createLine(0, 0, 0, 0, 0, 1, 0, 0, 0);
hideNode(axis)

head.makeTransform()
rotInt = vrInterpolator()
rotSlide = vrRotationAxisSlide(head, axis, 0, 359, 8.0)
rotInt.add(rotSlide)
rotInt.setActive(true)

##################################################
# define class to translate an object on x-axis. #
##################################################
class ActionTranslate(vrAEBase):
    tx = 0.0
    ty = 0.0
    tz = 0.0
    txs = 0.1
    def __init__(self, node):
        vrAEBase.__init__(self)
        self.addLoop()
        self.node = node
    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
    def loop(self):
        if self.isActive() == true:
            self.node.setTranslation(self.tx, self.ty, self.tz)
            self.tx = self.tx + self.txs

##################################################
# instantiate translation object and activate it #
##################################################
move = ActionTranslate(objb)
move.setActive(true)

##################################################
# output information about the collision #
##################################################
def printCollisionInfo(coll):
    useWorldSpace = True
    collidingNodes = coll.getCollidingNodes()
    print("Collision Nodes: First: " + str(collidingNodes[0]) + ", Second: " + str(collidingNodes[1]))
    collisionPosition = coll.getCollisionPoint(useWorldSpace)
    print("Collision Position: " + str(collisionPosition))
    collidingIndices = coll.getCollidingTriangleIndices()
    print("Colliding Triangle Indices: First: " + str(collidingIndices[0]) + ", Second: " + str(collidingIndices[1]))
    collidingTriangles = coll.getCollidingTriangles(useWorldSpace)
    print("Colliding Triangles: First: " + str(collidingTriangles[0]) + ", " + str(collidingTriangles[1]) + ", " + str(collidingTriangles[2]))
    print("Colliding Triangles: Second: " + str(collidingTriangles[3]) + ", " + str(collidingTriangles[4]) + ", " + str(collidingTriangles[5]))
    collisionInfo = coll.getCollisionInfo(useWorldSpace)
    print("Collision Info: Point: " + str(collisionInfo[0]))
    print("Collision Info: First Node: " + str(collisionInfo[1]) + ", Normal: " + str(collisionInfo[2]))
    print("Collision Info: Second Node: " + str(collisionInfo[3])  + ", Normal: " + str(collisionInfo[4]))

##################################
# generate collision object      #
# when collision happens reverse #
# the translation direction      #
##################################
coll1 = vrCollision([obja], [head])
coll1.connect("move.txs *= -1;coll1.setActive(false);coll2.setActive(true)")
coll1.connect(printCollisionInfo, coll1)

##################################
# generate collision object      #
# when collision happens reverse #
# the translation direction      #
##################################
coll2 = vrCollision([objc], [head])
coll2.connect("move.txs *= -1;coll1.setActive(true);coll2.setActive(false)")
coll2.connect(printCollisionInfo, coll2)
