# Move camera with joystick
# source: joystick-nav.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing move script!")

newScene()

def movedJoystick(js):
    #print js.getButtons()
    #print js.getAxes()

    # speed
    rotspeed = 0.01
    zoomspeed = 0.01
    panspeed = 0.1

    # buttons
    buttons = js.getButtons()

    if buttons & 1:
        setCameraPanning(panspeed, 0) # left
    if buttons & 8:
        setCameraPanning(-panspeed, 0) # right
    if buttons & 2:
        setCameraPanning(0, -panspeed) # up
    if buttons & 4:
        setCameraPanning(0, panspeed) # down
    
    # analog stick
    axes = js.getAxes()
    if len(axes) >= 2:
        #print axes[0], axes[1]
        setCameraRotation(-axes[0] * rotspeed, axes[1] * rotspeed)
        setCameraZoom(axes[2] * zoomspeed)

loadGeometry("$VRED_EXAMPLES/geo/car.osb")
updateScene()

joystick = vrJoystick()
joystick.connect(movedJoystick, joystick)

vrLogWarning("Use your joystick for navigation.")
