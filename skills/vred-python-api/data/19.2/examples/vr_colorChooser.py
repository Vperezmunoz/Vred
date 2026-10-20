# Interactive color manipulation in VR
# source: colorChooser.html

# © 2026 Autodesk, Inc. All rights reserved.

from PySide6 import QtCore, QtGui, QtWidgets

class ColorChooser():
    def __init__(self, parent=None):
        self.chooserEnabled = False
        self.colorTool = QtWidgets.QColorDialog()
        self.colorTool.setOption(QtWidgets.QColorDialog.ColorDialogOption.NoButtons,True)
        self.colorTool.currentColorChanged.connect(self.setColor)
        self.toolWidget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        self.title = QtWidgets.QLabel()
        font = self.title.font()
        font.setPointSize(11)
        self.title.setFont(font)
        layout.addWidget(self.title)
        layout.addWidget(self.colorTool)
        self.toolWidget.setLayout(layout)
        self.createMenu()
        self.material = None
        
    def setColor(self,value):
        if self.material == None:
            return
        cmd = "findMaterial('{}').fields().setVec3f('diffuseColor',{},{},{})".format(
            self.material.getName(),
            value.redF(),
            value.greenF(),
            value.blueF())
        vrSessionService.sendPython(cmd,self.material.getName() + ".diffuseColor")
    def pickNode(self,action,device):
        self.selectNode(device.pick().getNode())
    def selectNode(self,node):
        name = vrNodePtr(node).getName()
        # ignore VR panel
        if name == "VRMenuPanel":
            return
        self.node = node
        self.material = vrNodePtr(node).getMaterial()
        self.title.setText("Node: {} Material: {}".format(vrNodePtr(node).getName(),self.material.getName()))
        color = self.material.fields().getVec("diffuseColor",3)
        qcolor = QtGui.QColor(color[0]*255,color[1]*255,color[2]*255)
        self.colorTool.blockSignals(True)
        self.colorTool.setCurrentColor(qcolor)
        self.colorTool.blockSignals(False)
    def createMenu(self):
        icon = QtGui.QIcon()
        icon.addFile("colorChooser.png",QtCore.QSize(),QtGui.QIcon.Mode.Normal)
        self.tool = vrImmersiveUiService.createTool("CustomColorChooser")
        self.tool.setText("Color")
        self.tool.setIcon(icon)
        self.tool.setViewWidget(self.toolWidget)
        self.tool.signal().clicked.connect(self.enableChooser)
        self.tool.signal().viewClosed.connect(self.disableChooser)
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
    def enableChooser(self):
        if not self.chooserEnabled:
            pointer = vrDeviceService.getInteraction("Pointer")
            execute = pointer.getControllerAction("execute")
            execute.signal().triggered.connect(self.pickNode)
            self.chooserEnabled = True
    def disableChooser(self):
        if self.chooserEnabled:
            pointer = vrDeviceService.getInteraction("Pointer")
            execute = pointer.getControllerAction("execute")
            execute.signal().triggered.disconnect(self.pickNode)
            self.chooserEnabled = False

chooser = ColorChooser()
