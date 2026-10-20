# Hide Avatars in a collaboration session
# source: VRHideAvatarsModule.html

from PySide6 import QtCore, QtWidgets
from vrNodePtr import vrNodePtr

class HideAvatarsTool():
    def __init__(self):
        self.createMenu()
    def createMenu(self):
        # png icons as base64 string
        iconOn = "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"
        iconOff = "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"
        self.tool = vrImmersiveUiService.createTool("vrHideAvatarsTool")
        self.tool.setText("Show Avatars")
        self.tool.setCheckable(True)
        self.tool.setOnOffIconData(iconOn,iconOff)
        self.tool.setChecked(True)
        self.tool.signal().checked.connect(self.showAvatars)
        self.tool.signal().unchecked.connect(self.hideAvatars)
        self.tool.hideAway(True)
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
    def showAvatars(self):
        #vrSessionService.setAvatarProximityTransparentDistance(400)
        #vrSessionService.setAvatarProximityOpaqueDistance(1000)
        for user in vrSessionService.getRemoteUsers():
            for node in self.getAvatarNodes(user):
                vrNodePtr(node).setActive(True)
    def hideAvatars(self):
        #vrSessionService.setAvatarProximityTransparentDistance(1000000)
        #vrSessionService.setAvatarProximityOpaqueDistance(1000001)
        for user in vrSessionService.getRemoteUsers():
            for node in self.getAvatarNodes(user):
                vrNodePtr(node).setActive(False)
    def getAvatarNodes(self,user):
        return [user.getLeftHandNode(),user.getRightHandNode(),user.getHeadNode(),user.getTorsoNode()]
        
hideAvatarsTool = HideAvatarsTool()

label = QtWidgets.QLabel(VREDPluginWidget)
label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
label.setScaledContents(True)
label.setText("Python VR hide avatars tool\n" + __file__)
VREDPluginWidget.layout().addWidget(label)
