# Switch render window to fullscreen
# source: fullscreen.html

# © 2026 Autodesk, Inc. All rights reserved.

# a small test script to show how to display a fullscreen window with specified size
# special full screen mode
isFullscreen = false
def toggleFullscreen():
    width = 2560
    height = 1024
    global isFullscreen
    if isFullscreen == false:
        setRenderWindowDocked(0, false, NOBORDER)
        moveRenderWindow(0, 0, 0)
        resizeRenderWindow(0, width, height)
        isFullscreen = true
    else:
        setRenderWindowDocked(0, true, NOBORDER)
        isFullscreen = false

keySpace = vrKey(Key_Space, ControlButton)
keySpace.connect(toggleFullscreen)
