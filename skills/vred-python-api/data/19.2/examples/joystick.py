# vrJoystick demo
# source: joystick.html

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

def movedJoystick(js, node):
    #print js.getButtons()
    #print js.getAxes()

    # move speed
    step = 0.1

    # buttons
    buttons = js.getButtons()

    if buttons & 8:
        moveLeft(node, step)
    if buttons & 2:
        moveRight(node, step)
    if buttons & 1:
        moveUp(node, step)
    if buttons & 4:
        moveDown(node, step)
    
    # analog stick
    axes = js.getAxes()
    if len(axes) >= 2:
        if axes[0] < 0.0:
            moveLeft(node, abs(axes[0] * step))
        if axes[0] > 0.0:
            moveRight(node, abs(axes[0] * step))
        if axes[1] < 0.0:
            moveUp(node, abs(axes[1] * step))
        if axes[1] > 0.0:
            moveDown(node, abs(axes[1] * step))

loadGeometry("$VRED_EXAMPLES/geo/cube.osb")
updateScene()
setFromAtUp(0, 0.5,0.5,8,  0.5,0.5,0.5,  0,1,0)

# Searches for the node via regular expression.
cube = findNode("*cube*", true);
cube.makeTransform()

joystick = vrJoystick()
joystick.connect(movedJoystick, joystick, cube)

vrLogWarning("Use your joystick to move the object.")
