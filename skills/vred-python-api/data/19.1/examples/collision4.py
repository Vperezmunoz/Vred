# Collision Example 4
# source: collision4.html

# © 2026 Autodesk, Inc. All rights reserved.

# Collision demo

newScene()

obja = loadGeometry("$VRED_EXAMPLES/geo/car.osb")
obja.setName("Object_A")
obja.makeTransform()

objb = loadGeometry("$VRED_EXAMPLES/geo/cloth.osb")
objb.setName("Object_B")
objb.makeTransform()

updateScene()

#################################
# create collision object which #
# displays a message when both  #
# objects are colliding         #
# select a node and use the     #
# transform module to move them #
# around                        #
#################################
coll = vrCollision([obja], [objb])
coll.connect("print 'WUMM'")

print("just move Object_A so it collides with Object_B")
