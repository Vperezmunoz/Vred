# Attach callback to the event loop
# source: node.html

# © 2026 Autodesk, Inc. All rights reserved.

# This script is just a small debug script
# to demonstrate how to attach something into the event loop
print("Executing node script!")

newScene()
loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")
calcVertexNormals()

class MyEventLoopCB(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
    def loop(self):
        if self.isActive() == True:
            print("loop: nodename = " + self.node.getName() + " nodeid = " + str(self.node.getID()))

# create callback object and attach a node to it
myEventLoopCB = MyEventLoopCB()
myEventLoopCB.node = findNode("Nose");

# define key m to toggle activation of the loop callback
keyM = vrKey(Key_M)
keyM.connect(myEventLoopCB, SWITCH_TOGGLE)
keyM.connect("print('Toggled loop callback')")
print("Press key 'm' to toggle activation of the loop callback")

updateScene()
