# Collision Example 3
# source: collision3.html

# © 2026 Autodesk, Inc. All rights reserved.

# Collision demo

newScene()

#####################################################
# define special event class that only triggers     #
# when all supplied collision objects are colliding #
#####################################################
class CollisionAnd(vrAEBase):
    def __init__(self, cols):
        vrAEBase.__init__(self)
        self.addLoop()
        self.cols = cols
        self.setActive(true)
    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
    def loop(self):
        if self.isActive() == true:
            collide = 0
            l = len(self.cols)
            for i in range(l):
                if not self.cols[i].isColliding():
                    break
                else:
                    collide += 1
            if collide == l:
                self.callAllConnected()


########################
# create some geometry #
########################
obja = createBox(1, 1, 1, 1, 1, 1, 1, 0, 0, 0)
obja.makeTransform()
obja.setTranslation(-5, 0, 0)
obja.setName("Object_A")

objb = createBox(1, 1, 1, 1, 1, 1, 0, 1, 0, 0)
objb.makeTransform()
objb.setTranslation(5, 0, 0)
objb.setName("Object_B")

objc = createBox(1, 1, 1, 1, 1, 1, 0, 0, 1, 0)
objc.makeTransform()
objc.setTranslation(-5, 5, 0)
objc.setName("Object_C")

objd = createBox(1, 1, 1, 1, 1, 1, 0, 1, 1, 0)
objd.makeTransform()
objd.setTranslation(5, 5, 0)
objd.setName("Object_D")

updateScene()

#################################
# create some collision objects #
#################################
colla = vrCollision([obja], [objb])
collb = vrCollision([objc], [objd])

#########################################
# instantiate special collision object  #
# that only prints some special message #
# when obja collides with objb and objc #
# with objd                             #
#########################################
collab = CollisionAnd([colla, collb])
collab.connect("print 'WUMM!'")

print("just move Object_A so it collides with Object_B\n and Object_C so it collides with Object_D.")
