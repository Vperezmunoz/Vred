# Moving objects in VR
# source: objectMove.html

# © 2026 Autodesk, Inc. All rights reserved.

from PySide6 import QtCore, QtGui

class ObjectMover():
    def __init__(self):
        self.moverEnabled = False
        self.createMenu()
        self.node = None
    def startMove(self,action,device):
        self.node = self.getMovable(device.pick().getNode())
        if not self.node.isNull():
            vrSessionService.addNodeSync(self.node)
            self.constraint = vrConstraintService.createParentConstraint([device.getNode()],self.node,True)
    def stopMove(self,action,device):
        if not self.node == None and not self.node.isNull():
            vrSessionService.removeNodeSync(self.node)
            vrConstraintService.deleteConstraint(self.constraint)
    def createMenu(self):
        icon = QtGui.QIcon()
        icon.addFile("objectMoveOn.png",QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.On)
        icon.addFile("objectMoveOff.png",QtCore.QSize(),QtGui.QIcon.Mode.Normal,QtGui.QIcon.State.Off)
        self.tool = vrImmersiveUiService.createTool("CustomObjectMover")
        self.tool.setText("Move")
        self.tool.setCheckable(True)
        self.tool.setIcon(icon)
        self.tool.signal().checked.connect(self.enableMover)
        self.tool.signal().unchecked.connect(self.disableMover)
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
    def enableMover(self):
        if not self.moverEnabled:
            pointer = vrDeviceService.getInteraction("Pointer")
            start = pointer.getControllerAction("start")
            start.signal().triggered.connect(self.startMove)
            execute = pointer.getControllerAction("execute")
            execute.signal().triggered.connect(self.stopMove)
            self.moverEnabled = True
    def disableMover(self):
        if self.moverEnabled:
            pointer = vrDeviceService.getInteraction("Pointer")
            start = pointer.getControllerAction("start")
            start.signal().triggered.disconnect(self.startMove)
            execute = pointer.getControllerAction("execute")
            execute.signal().triggered.disconnect(self.stopMove)
            self.moverEnabled = False
    def getMovable(self,node):
        while not node.isNull():
            print((node.getName()))
            if node.getName().startswith("movable"):
                return node
            node = node.getParent()
        return node

mover = ObjectMover()
