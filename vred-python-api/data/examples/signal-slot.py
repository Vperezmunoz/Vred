# Render every frame
# source: signal-slot.html

# © 2026 Autodesk, Inc. All rights reserved.

# this example demonstrates how to force screen updates all the time

# define class that calls a render update every frame
class RenderAction(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
    def recEvent(self, state):
        vrAEBase.recEvent(self, state)
    def loop(self):
        if self.isActive():
            changeScenegraph()
            updateRender(true)

# create and activate render update object
render = RenderAction()
render.setActive(true)

# define key r to toogle the render update object
keyR = vrKey(Key_R)
keyR.connect(render, SWITCH_TOGGLE)
vrLogInfo("Press r to activate/deactivate the render update object")

# enable statistic to see that continous rendering is taking place
showStatistic(true)
