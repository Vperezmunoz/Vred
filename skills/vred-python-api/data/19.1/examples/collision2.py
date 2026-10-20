# Collision Example 2
# source: collision2.html

# © 2026 Autodesk, Inc. All rights reserved.

# Collision demo

newScene()

########################
# create some geometry #
########################

obja = createBox(1, 1, 1, 1, 1, 1, 1, 0, 0, 0)
obja.makeTransform()
obja.setTranslation(-5, 0, 0)

objb = createBox(1, 1, 1, 1, 1, 1, 0, 1, 0, 0)
objb.makeTransform()
objb.setTranslation(5, 0, 0)

objc = createBox(1, 1, 1, 1, 1, 1, 0, 0, 1, 0)
objc.makeTransform()
objc.setTranslation(-5, 5, 0)

objd = createBox(1, 1, 1, 1, 1, 1, 0, 1, 1, 0)
objd.makeTransform()
objd.setTranslation(5, 5, 0)

updateScene()

##################################
# create a collision object that #
# prints a message if any of the #
# supplied objects collide       #
##################################

coll = vrCollision([obja, objb, objc, objd], [obja, objb, objc, objd])
coll.connect("print 'WUMM'")

print("just move any box so it collides another one.")
