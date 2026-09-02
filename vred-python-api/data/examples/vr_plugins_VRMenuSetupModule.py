# Allowing to configure the VR menu
# source: VRMenuSetupModule.html

from PySide6 import QtCore, QtWidgets, QtGui, QtQuickWidgets
from shiboken6 import wrapInstance
from vrKernelServices import vrdImmersiveMenu

def getIcon(name):
    icon = QtGui.QIcon()
    iconPath = "resources:" + name
    icon.addPixmap(QtGui.QPixmap("{}".format(iconPath)), QtGui.QIcon.Normal)
    return icon

class VRSetupMenu(QtCore.QObject):
    def __init__(self, parent=None):
        super(VRSetupMenu, self).__init__(parent)
        self.settings = QtCore.QSettings("Autodesk","VRED")
        QtCore.QTimer.singleShot(1, self.init)
        self.menuName = QtCore.QCoreApplication.translate("QVRDockWindowManager","Scripts")
        self.m_qmlMenu = None
        self.m_quickWidget = None
    def init(self):
        self.createMenu()
        vrFileIOService.newScene.connect(self.updateMenu)
        vrFileIOService.projectLoaded.connect(self.onProjectLoaded)
    def __del__(self):
        if self.m_qmlMenu is not None:
            vrImmersiveUiService.deleteMenu(self.m_qmlMenu)
            self.m_qmlMenu = None
            self.m_quickWidget = None
        self.destroyMenu()
    def createToolsActions(self,tools,internal):
        for tool in tools:
            if tool.getIsInternal() != internal:
                continue
            action = QtGui.QAction(tool.getText(), self.mw)
            action.setCheckable(True)
            key = "VRMenu_"+tool.getName();
            if self.settings.contains(key):
                hideAway = bool(self.settings.value(key,"false") == "true")
            else:
                hideAway = tool.getHideAway()
            tool.hideAway(hideAway)
            action.setChecked(not hideAway)
            action.setProperty("tool",tool.getName())
            action.toggled.connect(self.actionTriggered)
            self.menu.addAction(action)
    def createMenu(self):
        self.mw = wrapInstance(VREDMainWindowId, QtWidgets.QMainWindow)
        self.menu = QtWidgets.QMenu("VR Menu", self.mw)
        self.menu.setIcon(getIcon("Various/TransparentIcon.svg"))
        self.menu.setTearOffEnabled(True)
        showAllAction = QtGui.QAction("Show All Tools", self.mw)
        hideAllAction = QtGui.QAction("Hide All Tools", self.mw)
        self.menu.addAction(showAllAction)
        self.menu.addAction(hideAllAction)
        self.menu.addSeparator()
        showAllAction.triggered.connect(self.showAll)
        hideAllAction.triggered.connect(self.hideAll)
        tools = sorted(vrImmersiveUiService.getTools(), key=lambda tool: tool.getName())
        self.createToolsActions(tools,True)
        self.menu.addSeparator()
        self.createToolsActions(tools,False)
        self.menu.addSeparator()
        showStatusAction = QtGui.QAction("Show Status Panel", self.mw)
        showStatusAction.setCheckable(True)
        showStatusAction.setChecked(not vrImmersiveUiService.getHideStatusVRPanel())
        showStatusAction.toggled.connect(self.showStatus)
        self.menu.addAction(showStatusAction)
        showParticipantsAction = QtGui.QAction("Show Participants Panel", self.mw)
        showParticipantsAction.setCheckable(True)
        showParticipantsAction.setChecked(not vrImmersiveUiService.getHideParticipantsVRPanel())
        showParticipantsAction.toggled.connect(self.showParticipants)
        self.menu.addAction(showParticipantsAction)
        self.menu.addSeparator()
        showVRMenuAction = QtGui.QAction("Show VR Menu", self.mw)
        showVRMenuAction.setCheckable(True)
        showVRMenuAction.setChecked(False)
        showVRMenuAction.toggled.connect(self.showVRMenu)
        self.menu.addAction(showVRMenuAction)
        showCircularMenuAction = QtGui.QAction("Show Circular Menu", self.mw)
        showCircularMenuAction.setCheckable(True)
        showCircularMenuAction.setChecked(False)
        showCircularMenuAction.toggled.connect(self.showCircularMenu)
        self.menu.addAction(showCircularMenuAction)
        for action in self.mw.menuBar().actions():
            if action.text() == self.menuName:
                scriptMenu = action.menu()
                first = scriptMenu.actions()[0];
                scriptMenu.insertAction(first, self.menu.menuAction())
                self.separator = scriptMenu.insertSeparator(first)
                break
    def destroyMenu(self):
        for action in self.mw.menuBar().actions():
            if action.text() == self.menuName:
                action.menu().removeAction(self.menu.menuAction())
    def actionTriggered(self,checked):
        action =  self.sender()
        toolName = action.property("tool")
        tool = vrImmersiveUiService.findTool(toolName)
        tool.hideAway(not checked)
        self.settings.setValue("VRMenu_"+tool.getName(),tool.getHideAway())
        self.settings.sync()
    def showAll(self):
        for action in self.menu.actions():
            if not action.property("tool") == None:
                action.setChecked(True)
    def hideAll(self):
        for action in self.menu.actions():
            if not action.property("tool") == None:
                action.setChecked(False)
    def showStatus(self,checked):
        vrImmersiveUiService.setHideStatusVRPanel(not checked)
    def showParticipants(self,checked):
        vrImmersiveUiService.setHideParticipantsVRPanel(not checked)
    def updateMenu(self):
        self.destroyMenu()
        self.createMenu()
    def onProjectLoaded(self):
        QtCore.QTimer.singleShot(0, self.updateMenu)
    def showVRMenu(self,checked):
        if not checked:
            vrImmersiveUiService.showMenuIconBar(False,False)
            return
        vrImmersiveUiService.showMenuIconBar(True,False)
        menuIconBar = vrImmersiveUiService.findMenu("MenuIconBar")
        menuIconBar.setOrigin(vrdImmersiveMenu.MenuOrigin.ORIGIN_LOCAL)
        menuIconBar.setDepth(3)
        menuIconBar.setWidth(200)
        menuIconBar.setTranslation(0,400,-150)
        menuIconBar.setRotation(0,0,0)
        menuIconBar.setOrigin(vrdImmersiveMenu.MenuOrigin.ORIGIN_CAMERA)
    def showCircularMenu(self,checked):
        vrImmersiveUiService.showCircularMenu(checked)

menuSetup = VRSetupMenu()

label = QtWidgets.QLabel(VREDPluginWidget)
label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter);
label.setScaledContents(True)
label.setText("Python VR menu configure tool\n" + __file__)
VREDPluginWidget.layout().addWidget(label)
