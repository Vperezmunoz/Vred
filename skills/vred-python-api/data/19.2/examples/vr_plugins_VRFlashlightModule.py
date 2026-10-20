# Showing a flash light in VR
# source: VRFlashlightModule.html

from PySide6 import QtCore,QtWidgets
from vrScenegraph import *
from vrController import *
from vrNodePtr import *
from vrNodeUtils import *
from vrFileIO import *
#test
class Flashlight():
    def __init__(self):
        QtCore.QTimer.singleShot(0, self.init)
    def init(self):
        self.geo = None
        self.on = False
        self.createMenu()
        pointer = vrDeviceService.getInteraction("Main Menu")
        start = pointer.getControllerAction("showMainMenu")
        start.signal().triggered.connect(self.onMenuOpened)
        self.handNode = vrDeviceService.getVRDevice("right-controller").getNode()
        self.activeController = vrDeviceService.getVRDevice("right-controller")
        self.isLeftSide = False
        vrHMDService.hmdStatusWillChange.connect(self.__onHMDStatusWillChange)
    def onMenuOpened(self,action,device):
        # place the flashlight on the other hand
        if device.getName() == "left-controller":
            self.handNode = vrDeviceService.getVRDevice("right-controller").getNode()
            self.activeController = vrDeviceService.getVRDevice("right-controller")
            self.isLeftSide = False
        else:
            self.handNode = vrDeviceService.getVRDevice("left-controller").getNode()
            self.activeController = vrDeviceService.getVRDevice("left-controller")
            self.isLeftSide = True
    def switchOn(self):
        if not self.on:
            self.getGeo().setActive(True)
            self.on = True
            # move the flashlight with the hand
            self.constraint = vrConstraintService.createParentConstraint([self.handNode],self.geo,False)
            self.constraint.setVisualizationVisible(False)
            self.activeController.signal().moved.connect(self.updateFlashlight)
            self.visualizationMode = self.activeController.getVisualizationMode()
            self.adjustFlashlight(self.activeController)
    def switchOff(self):
        if self.on:
            self.getGeo().setActive(False)
            self.on = False
            vrConstraintService.deleteConstraint(self.constraint)
            self.activeController.signal().moved.disconnect(self.updateFlashlight)
    def createMenu(self):
        # png icons as base64 string
        onIcon = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAMAAAC5zwKfAAAAilBMVEX9oRTreSj6twb3qw3ylxjtfibvlBv1pBHxjB/rfSjviiDvix/7vQPxkxvugiPtfiXwix/0nBXuhSL1oRLwjB7rfCf0qQ7ugyP8wQH4swn1pRDwix/ylBn0nBXwiCHtgST1pBHvih/7uwT5tAj4rgv7wAH1oRPvix77ugXuhCP0oBP1oxHwjh3uhCJVyFMlAAAAK3RSTlMAM/////4QJEKBpVHxjTq5FrBj8NjEG+exwjzY7eWF7tbo3eTcTFj8W26hmZCkDQAAAAlwSFlzAAAk6QAAJOkBUCTn+AAAA31JREFUWAntWO12ojAQDUkIVJRGrEpXrVq7220T3v/19uYDRIviYvqvOT1lmjA3dzKTmaGEDB8RxWCMKcUV51xXGPFwOGgeERXjWhvE+wAFEMEQFJMofUj1KIvvAyQkGTuTxSTLxaMc3Q1orVaMiWmRPYhI3w8IRHCkBGBaPP4HoBRH97VE45mZUko8wSty3uMUOZE1yoKqRk4eGtEuJ1ypfImwyZY9gCV9rgF/URrV8kpPatE9YTXgbNhcP8OSUulVM6oWXoy4LrxYP8CxDsOrYSOZqrnkVNUMJ0ovTk8R58g84nWGZMq4UxUp5R5QMDaqmR2fkb96PYApValTSqn2Jmeshj7CEURNBaPhk6smE7JWnk1OtWe4oVUbqZGTm+5yybm0Kg1gxNi5SzxmFN/AUHLvFpicWMUXxtwWHqb1SLb9JpMd21u3INScyYzNWxinYhJjnE59+Stz3oWXlWWYU5Z/eamZiPoBxWtsGUq6tWoJ3TXqHQIQO2bvmUqGALpYv7BtfZ+6l0X5+nrYvL1tnja79f5pv1otV8v9XHa/fcPsb1PWMFA0UNmYMrHLq/hCIPYDij8OzwListqMou8AJAAcz2ZUzTC4fn/fr3FZ4+EMcec7zeie7Xz1bFIs5JchZLu8nCn0/Zn6M0Rho6bZUBr9RlxlfXoX1zMHyOAV4xOX5uP4yuW7COUWxNggumbDtkM2h1aLHrUryyhT53hVvLyi0Lf0t2bIXMNm+ytfFfp0u9efwRAc7U0xRwjEewgSIhubDUUDGMvurW+dNT2lZVi7eXjM+C0Lb7H38setTC6/92mOkSqKfMP14+X3bl4Rk3JUj5fh17i1H0Can9b0cDEtMDLzqxh+6drb47ogEHGAVXW5JrcV+uSpDRwThYEADUOTbsAwhJMJsQxt0xuOIThak8MwRGRjhD3DQy5EtOTBTD64QFgFApxSl2FEHgiwpK55JSIYYP1dEghw2nxPBQIs6UKk03kezORPKlHxuU7DnaF8ZvgcnpNAJoPh1AKGY5jBZMbzHCRDjE86Flm5ysQ2kMnIh4dM4i6HytgANNnGtA1hTLaAps6HZGhLQECGtqbgX2XBTA5bRs0Z+qoXjKGt9MEK/bd5OVjYFP4M0ToM/g49SQFike+QbZAQkyDtIcBFgWTDAnTDDVFRbNYfoeg1qD/Czwl82wn8A1RuSwNXqFYLAAAAAElFTkSuQmCC"
        offIcon = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAMAAAC5zwKfAAAAe1BMVEWwsbWwsrO1triwsbOur7Gmp6men6GdnqCcnp64ubu1t7ump6mkpKavr7GkpaenqKqmpqm7u72kpaesrK+jpKa0tbeztbeztLWgoaOfoKGoqaurrK+5ury6vL2vsLKnqKqcnZ+trrCbm6CjpKaxsrSmqKi6ur2ioqS5ubt/L2nWAAAAKXRSTlMAI//+/v/+/DFcLkOGZ5KkE6/qHNfsTLP9Ylbq3e7d2sTrM7jMYbN2V7lTpSMAAAAJcEhZcwAAJOkAACTpAVAk5/gAAAMoSURBVFgJ7Zh7c6MgEMBxEVPFJIh4tbVec73n9/+EtzxWc0mrNnAz/aM708AY+LkvdkkZu10yIOE8z4WVYnc7DnfezUBwvFggKz2R86qS9V4cyqKI0pAxbzXn7CilOmaHSJNnq1lT7msm83hg8KNSUgt2FNtNbtVbzpEC0GSDQVGmWNawrVuitAATsa0reuzGrAMuNabN3qxo2IChnV8A7mhuxD1N/VjllIb9soYPAKTLI0AWKK0Q5b9AJrucEnsxbSqAOmyVs4ZNLtQFkFWC28TuVzRkDXTXQM4vLLZLKmGPXr92UvAg7D0RNQwm7wFkeMv5IDsEFmsasgEOEzAExcBwDprmFQLXi8M9gM+cyYeYP0HpCRUmlV73IcPtPiwI9ORmsv0SyOSAXlwrX0+g3cYScp9BHTRXJHpQ6WK3BnwE4UAyjBim10ISkBKJRH9jVKN20cXRraj4dHhe2yH1GvC1XUvPpH/v0pJ3frfgEEtqxrEzX587YzptumdtjNb6pN75knk5VgdqGlhPODU2OuDzwq2zCQiAQM/DkndZbLbiGHPAEWBE6YZvw4AGa727Hbj91RtXqlah4EdVqSyIajO1cfv1MqzTk4SQ2Ipyu8lYEibBmLioYMlbybVrxeYnEw7gLMrUXeZ1m2cmEPmUNr0Qi6d5BY3FhZCkYS8iLGbsiYBosvdhEaMgY+oMGGIS4UHrjxci0tmLMtgS6TxjHtpUvL0wWJgTbEsoGGe8SMNRhacRg6oblKOVwyEBj1RJiCr3Zen+6jI6Ik4970T0Y14cSd+okYBYaE5RINocwmzvQt/pWdToga6lnKJAtDkArYZJgXhMimTApxfFpBF9KuDordd9qrQJXUkm82H4taKS+VB5k1kyIP2eShYUxcrGYGFIB8Tul2O3S2aywv6cYz9OB2yw0YuTSpY2Ei85QkiZrtoo+cP8ZDqZhgCP+F8Kk77aJNTQRvlD10Pb8lDBZHlo7yIWmOjo/bI8Jx8byPECm8iH3uSEffm3858LSoLrpi3+mcS7e57rP5HX69BI7ID34jxPpJ7DqodxSMk70/Vz+umB/+GBv9HkI1uzfxLJAAAAAElFTkSuQmCC"
        self.tool = vrImmersiveUiService.createTool("vrFlashlightTool")
        self.tool.setText("Flashlight")
        self.tool.setCheckable(True)
        self.tool.setOnOffIconData(onIcon,offIcon)
        self.tool.signal().checked.connect(self.switchOn)
        self.tool.signal().unchecked.connect(self.switchOff)
        self.tool.hideAway(True)
    def deleteMenu(self):
        vrImmersiveUiService.deleteTool(self.tool)
    def getGeo(self):
        if not self.geo is None and  self.geo.isValid():
            return self.geo
        self.createGeo()
        return self.geo
    def createGeo(self):
        for node in findNodes("VR_Flashlight"):
            node.getParent().subChild(node)
        rootNode = getInternalRootNode()
        self.geo = createNode("Transform3D","VR_Flashlight", rootNode, False)
        self.trans = createNode("Transform3D","FlashlightPos",self.geo,False)
        self.loadModel()
        self.flashlightHandle = vrNodeService.findNode("Housing_02", False, False, self.trans)
        self.geo.setActive(False)
        setIsVRNode(self.trans, True)
        setIsVRNode(self.geo, True)
    def loadModel(self):
        path = vrFileIOService.getVREDDataDir() + "/Internal/VR/Flashlight.osb"
        files = [path]
        nodes = loadOSB(files)
        for node in nodes:
            self.trans.addChild(node)
    def removeGeo(self):
        subChilds(self.geo.getParent(),[self.geo])
    def updateFlashlight(self, device):
        if device.getVisualizationMode() != self.visualizationMode:
            self.adjustFlashlight(device)
            self.visualizationMode = device.getVisualizationMode()
    def adjustFlashlight(self, device):
        if device.getVisualizationMode() == 1:
            self.setHandTransform()
            self.flashlightHandle.setVisibilityFlag(True)
        else:
            self.setControllerTransform()
            self.flashlightHandle.setVisibilityFlag(False)

    def setHandTransform(self):
        if self.isLeftSide:
            setTransformNodeTranslation(self.trans,-17,-5,60,False)
            setTransformNodeRotation(self.trans,180,10,0)
        else:
            setTransformNodeTranslation(self.trans,17,-5,60,False)
            setTransformNodeRotation(self.trans,180,-10,0)

    def setControllerTransform(self):
        setTransformNodeTranslation(self.trans,0,-50,50,False)
        setTransformNodeRotation(self.trans,110,0,0)

    def __onHMDStatusWillChange(self, active):
        if not active:
            self.tool.setChecked(False)
            self.switchOff()

flashlight = Flashlight()

label = QtWidgets.QLabel(VREDPluginWidget)
label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
label.setScaledContents(True)
label.setText("Python VR flashlight avatars tool\n" + __file__)
VREDPluginWidget.layout().addWidget(label)
