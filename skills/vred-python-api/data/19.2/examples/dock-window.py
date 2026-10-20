# Manipulate docking state of render window
# source: dock-window.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing dock-widget script!")

class ActionToggleDock(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
        if self.isActive():
            for i in range(getRenderWindowCount()):
                setRenderWindowDocked(i, true)
        else:
            for i in range(getRenderWindowCount()):
                setRenderWindowDocked(i, false, NOBORDER)
            moveRenderWindow(0, 0, 0)
            resizeRenderWindow(0, 640, 512)
            moveRenderWindow(1, 640, 0)
            resizeRenderWindow(1, 640, 512)
            moveRenderWindow(2, 0, 512)
            resizeRenderWindow(2, 640, 512)
            moveRenderWindow(3, 640, 512)
            resizeRenderWindow(3, 640, 512)

dock = ActionToggleDock()

keySpace = vrKey(Key_Space)
keySpace.connect(dock, SWITCH_TOGGLE)

# destroy all render windows
for i in range(getRenderWindowCount()):
    destroyRenderWindow(0)

for i in range(4):
    createRenderWindow()

dock.setActive(true)

print("End")
