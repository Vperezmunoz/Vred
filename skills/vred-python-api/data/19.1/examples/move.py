# Move object with keys
# source: move.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing move script!")

newScene()

def moveLeft(node, step):
    pos = node.getTranslation()
    node.setTranslation(pos[0] - step, pos[1], pos[2])

def moveRight(node, step):
    pos = node.getTranslation()
    node.setTranslation(pos[0] + step, pos[1], pos[2])

def moveUp(node, step):
    pos = node.getTranslation()
    node.setTranslation(pos[0], pos[1] + step, pos[2])

def moveDown(node, step):
    pos = node.getTranslation()
    node.setTranslation(pos[0], pos[1] - step, pos[2])

loadGeometry("$VRED_EXAMPLES/geo/cube.osb")
updateScene()

# Searches for the node via regular expression.
cube = findNode("*cube*", true);
cube.makeTransform()

# move speed
step = 100

keyA = vrKey(Key_A)
keyA.connect(moveLeft, cube, step)

keyD = vrKey(Key_D)
keyD.connect(moveRight, cube, step)

keyW = vrKey(Key_W)
keyW.connect(moveUp, cube, step)

keyS = vrKey(Key_S)
keyS.connect(moveDown, cube, step)

vrLogWarning("Press key W, A, S, D to move the object.")
