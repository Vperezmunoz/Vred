# Example UI for implementing a scatter tool
# source: ScatterTool.html

"""
Scatter Tool Plugin for VRED

This script plugin creates a UI for scattering and placing objects in the scene.

Usage:
   1. Create one or more groups in the scenegraph containing the geometries to clone.
      Ensure the scale and rotate pivots of the groups are set correctly.
   2. Select the groups in the scene graph and click "Set Source Objects".
   3. Optionally select a target group and click "Set Target Group".
   4. Configure the scatter parameters (count, radius, rotation, scale).
   5. Click "Start Placement Mode" to begin placement.
   6. Click on the scene to scatter objects around the clicked position.
   7. Click "Stop Placement Mode" to end placement.
"""

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtCore import Signal, Slot, QObject

import ctypes
import random
import math
import os
import json

import uiTools
from vrController import *
from vrAEBase import vrAEBase
from vrScenegraph import *
from vrOSGWidget import *
from vrNodePtr import *
from vrNodeUtils import *
from vrOSGTypes import *

# Services (PySide-injected globals); fall back to None if not present in this context
try:
    vrScenegraphService
except NameError:
    vrScenegraphService = None

try:
    vrScenegraphTypes
except NameError:
    from vrScenegraph import vrScenegraphTypes  # type: ignore


# Load the .ui file
try:
    ScatterTool_form, ScatterTool_base = uiTools.loadUiType('ScatterTool.ui')
except Exception as e:
    print("ScatterTool: Error loading UI file: {}".format(str(e)))
    import traceback
    traceback.print_exc()
    # Provide fallback so the script doesn't crash
    class ScatterTool_form(object):
        """Fallback UI form with a no-op setup."""
        def setupUi(self, _):
            pass
    ScatterTool_base = QtWidgets.QWidget

# Windows virtual key codes for mouse buttons
LEFTCLICK = 0x01
RIGHTCLICK = 0x02


def getIcon(name):
    """Returns a QIcon for a button or action."""
    icon = QtGui.QIcon()
    iconPath = "resources:General/" + name
    icon.addPixmap(QtGui.QPixmap("{}Disabled.svg".format(iconPath)), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
    icon.addPixmap(QtGui.QPixmap("{}OffNormal.svg".format(iconPath)), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    return icon


class ScatterSettings:
    """Holds all scatter configuration settings."""
    def __init__(self):
        self.applyRandomRotation = True
        self.applyRandomScale = True
        self.minimumScaleSpinBox = 1.0
        self.maximumScaleSpinBox = 3.0
        self.objectsPerClick = 64
        self.scatterRadius = 1000.0
        self.seed = 0xfea1dab8
        self.distributionMode = "Random"  # "Random" or "Halton"

    def toDict(self):
        """Convert settings to a dictionary for serialization."""
        return {
            'applyRandomRotation': self.applyRandomRotation,
            'applyRandomScale': self.applyRandomScale,
            'minimumScaleSpinBox': self.minimumScaleSpinBox,
            'maximumScaleSpinBox': self.maximumScaleSpinBox,
            'objectsPerClick': self.objectsPerClick,
            'scatterRadius': self.scatterRadius,
            'seed': self.seed,
            'distributionMode': self.distributionMode
        }

    def fromDict(self, data):
        """Load settings from a dictionary."""
        self.applyRandomRotation = data.get('applyRandomRotation', True)
        self.applyRandomScale = data.get('applyRandomScale', True)
        self.minimumScaleSpinBox = data.get('minimumScaleSpinBox', data.get('minimumScale', 1.0))
        self.maximumScaleSpinBox = data.get('maximumScaleSpinBox', data.get('maximumScale', 3.0))
        self.objectsPerClick = data.get('objectsPerClick', 64)
        self.scatterRadius = data.get('scatterRadius', 1000.0)
        self.seed = data.get('seed', 0xfea1dab8)
        self.distributionMode = data.get('distributionMode', "Random")


class ScatterEngine(QObject):
    """
    Core scatter/placement logic.
    Handles the actual object placement based on the configured settings.
    """
    placementStateChanged = Signal(bool)
    sourceObjectsChanged = Signal()
    targetGroupChanged = Signal()

    def __init__(self, settings):
        super(ScatterEngine, self).__init__()
        self.settings = settings
        self.placeNode = None  # Will be set when placement starts
        self.sourceObjects = []  # List of source objects to scatter
        self.targetGroup = None  # Target group for scattered objects
        self.autoCreatedGroup = None  # Auto-created group if no target is set
        self.placementActive = False
        self.leftButtonState = 0x0
        self.mouseListener = None
        self.haltonIndex = 1

        # Initialize the random number generator
        self.resetRandomSeed()

    def resetRandomSeed(self):
        """Re-initialize the random number generator with the current seed."""
        random.seed(self.settings.seed)
        self.haltonIndex = 1

    def halton(self, index, base):
        """Generate a Halton sequence value for the given index and base."""
        result = 0.0
        f = 1.0
        i = index
        while i > 0:
            f /= base
            result += f * (i % base)
            i //= base
        return result

    def getUniformDiskSample(self, u, v):
        """Returns a 2D sample distributed uniformly on a disk."""
        r = math.sqrt(u)
        theta = 2.0 * math.pi * v
        x = math.sin(theta)
        y = math.cos(theta)
        return QVector2D(x * r, y * r)

    def nextScatterSample(self):
        """Return a 2D sample using configured distribution."""
        if self.settings.distributionMode == "Halton":
            u = self.halton(self.haltonIndex, 2)
            v = self.halton(self.haltonIndex, 3)
            self.haltonIndex += 1
        else:
            u = random.random()
            v = random.random()
        return self.getUniformDiskSample(u, v)

    def createClonedAsset(self, positions):
        """Create clones for all provided positions in a single batch."""
        if not self.sourceObjects or not positions:
            return

        # Collect source nodes to clone for each position (one source per position)
        nodes_to_clone = []
        position_map = []
        for pos in positions:
            sourceNode = random.choice(self.sourceObjects)
            if sourceNode.isValid():
                nodes_to_clone.append(sourceNode)
                position_map.append(pos)

        if not nodes_to_clone:
            return

        # Clone via vrNodeService (new API) using a single batch call
        clonedNodes = vrNodeService.cloneNodes(nodes_to_clone)
        if not clonedNodes:
            return

        # Prepare parent group once
        parentGroup = self.getOrCreateTargetGroup()

        # Apply transforms to each cloned node and collect for moving
        validClones = []
        for pos, clonedNode in zip(position_map, clonedNodes):
            if not clonedNode.isValid():
                continue

            if self.settings.applyRandomRotation:
                rotationRnd = random.random()
                clonedNode.setRotationAsEuler(QVector3D(0.0, 0.0, rotationRnd * 360.0))

            if self.settings.applyRandomScale:
                scaleRnd = random.random()
                scale = self.settings.minimumScaleSpinBox + scaleRnd * (self.settings.maximumScaleSpinBox - self.settings.minimumScaleSpinBox)
                clonedNode.setScale(QVector3D(scale, scale, scale))

            localRotatePivot = clonedNode.getRotatePivot()
            centerPosition = pos - localRotatePivot
            clonedNode.setWorldTranslation(centerPosition)

            validClones.append(clonedNode)

        if parentGroup is not None and parentGroup.isValid() and validClones:
            vrNodeService.moveTo(parentGroup, validClones)

    def getOrCreateTargetGroup(self):
        """Get the target group or create a new one if not set."""
        if self.targetGroup is not None and self.targetGroup.isValid():
            return self.targetGroup

        # Create a new group if we haven't already
        if self.autoCreatedGroup is None or not self.autoCreatedGroup.isValid():
            # Create a new group under the root
            if vrScenegraphService is not None:
                createdGroup = vrScenegraphService.createNode(
                    vrScenegraphTypes.TransformNode,
                    vrScenegraphService.getRootNode(),
                    "ScatteredObjects"
                )
                self.autoCreatedGroup = createdGroup
            else:
                createdGroup = createNode("Group", "ScatteredObjects")
                self.autoCreatedGroup = vrNodeService.getNodeFromId(createdGroup.getID())
        return self.autoCreatedGroup

    def ensureTargetGroupPresent(self):
        """Ensure the target group is still valid/in the scenegraph when placement occurs."""
        if self.targetGroup is not None:
            if self.targetGroup.isValid():
                # make sure the target group is still in the scenegraph
                foundNode = vrNodeService.findNode(self.targetGroup.getName(), False, False, vrScenegraphService.getRootNode())
                if not foundNode.isValid():
                    vrLogWarning("ScatterTool: Target group was removed from the scenegraph; falling back to auto-create.")
                    self.targetGroup = None
            else:
                vrLogWarning("ScatterTool: Target group is not valid; falling back to auto-create.")
                self.targetGroup = None
        if self.targetGroup is None:
            if self.autoCreatedGroup is not None:
                if self.autoCreatedGroup.isValid():
                    # make sure the auto created group is still in the scenegraph
                    foundNode = vrNodeService.findNode(self.autoCreatedGroup.getName(), False, False, vrScenegraphService.getRootNode())
                    if not foundNode.isValid():
                        self.autoCreatedGroup = None
                else:
                    self.autoCreatedGroup = None



    def placeClone(self):
        """Place clones at the current mouse position."""
        self.ensureTargetGroupPresent()
        mousePosition = getMousePosition(-1)

        # Check if the mouse position is valid
        if mousePosition[0] < 0 or mousePosition[1] < 0:
            return

        # Temporarily adjust near and far clipping planes to avoid numerical instabilities
        currentNear = getNear()
        currentFar = getFar()
        setNear(10000.0)
        setFar(1000000.0)

        # Calculate the viewing ray at the current mouse position
        [rayOrg, rayDir] = getViewRay(-1, mousePosition[0], mousePosition[1])
        setNear(currentNear)
        setFar(currentFar)

        rayFrom = getFrom(-1)
        [hitNode, hitPoint, hitNormal, hitUV] = getSceneIntersection(-1, rayFrom, rayDir)

        if hitNode.isValid():
            placePositions = []
            zOffset = self.settings.scatterRadius
            vrdHitNode = vrNodeService.getNodeFromId(hitNode.getID())
            if vrdHitNode.isValid():
                hitNodeBB = vrdHitNode.getWorldBoundingBox()
                if hitNodeBB.isValid():
                    zOffset = hitNodeBB.getSize().z() + self.settings.scatterRadius

            for idx in range(0, self.settings.objectsPerClick):
                offsetRnd = self.nextScatterSample()
                if self.settings.objectsPerClick == 1:
                    offsetRnd = QVector2D(0.0, 0.0)
                [offsetHitNode, offsetHitPoint, offsetHitNormal, offsetHitUV] = getSceneIntersection(
                    -1,
                    Pnt3f(
                        hitPoint.x() + self.settings.scatterRadius * offsetRnd.x(),
                        hitPoint.y() + self.settings.scatterRadius * offsetRnd.y(),
                        hitPoint.z() + zOffset
                    ),
                    Vec3f(0.0, 0.0, -1.0)
                )

                if offsetHitNode.isValid() and offsetHitNode.getID() == hitNode.getID():
                        placePositions.append(QVector3D(offsetHitPoint.x(), offsetHitPoint.y(), offsetHitPoint.z()))
            
            if len(placePositions) == 0:
                placePositions.append(QVector3D(hitPoint.x(), hitPoint.y(), hitPoint.z()))
            self.createClonedAsset(placePositions)

    def setSourceObjects(self):
        """Set the currently selected nodes as source objects for scattering."""
        if vrScenegraphService is not None:
            selectedNodes = vrScenegraphService.getSelectedNodes()
        else:
            selectedNodes = getSelectedNodes()
        if not selectedNodes:
            vrLogWarning("ScatterTool: Please select one or more nodes in the scenegraph first.")
            return False

        filteredNodes = []
        for node in selectedNodes:
            if not node.isValid():
                continue
            
            if node.isType(vrdGeometryNode):
                vrLogWarning("ScatterTool: Source nodes must be group nodes, not geometry: {}".format(node.getName()))
                continue
            filteredNodes.append(node)

        self.sourceObjects = filteredNodes
        if not self.sourceObjects:
            vrLogWarning("ScatterTool: No valid nodes selected.")
            return False

        self.sourceObjectsChanged.emit()
        return True

    def getSourceObjectNames(self):
        """Get names of source objects."""
        if not self.sourceObjects:
            return "None"
        validNames = [node.getName() for node in self.sourceObjects if node.isValid()]
        if not validNames:
            return "None (invalid)"
        return ", ".join(validNames[:3]) + ("..." if len(validNames) > 3 else "")

    def setTargetGroup(self):
        """Set the currently selected node as the target group for scattered objects."""
        if vrScenegraphService is not None:
            selectedNode = vrScenegraphService.getSelectedNode()
        else:
            selectedNode = getSelectedNode()
        if selectedNode is None or not selectedNode.isValid():
            vrLogWarning("ScatterTool: Please select a group node in the scenegraph first.")
            return False

        if vrScenegraphService is not None:
            self.targetGroup = selectedNode
        else:
            self.targetGroup = vrNodeService.getNodeFromId(selectedNode.getID())
        self.autoCreatedGroup = None  # Clear auto-created group when user sets a target
        self.targetGroupChanged.emit()
        return True

    def clearTargetGroup(self):
        """Clear the target group setting."""
        self.targetGroup = None
        self.targetGroupChanged.emit()

    def getTargetGroupName(self):
        """Get the name of the target group."""
        if self.targetGroup is not None and self.targetGroup.isValid():
            return self.targetGroup.getName()
        return "Auto-create"

    def validateSourceObjects(self):
        """Validate that source objects are still valid."""
        if not self.sourceObjects:
            return False
        # Filter out invalid nodes
        self.sourceObjects = [node for node in self.sourceObjects if node.isValid()]
        return len(self.sourceObjects) > 0

    def startPlacement(self):
        """Start placement mode."""
        if self.placementActive:
            return False

        # Validate source objects
        if not self.validateSourceObjects():
            vrLogWarning("ScatterTool: No valid source objects. Please set source objects first.")
            return False

        self.placementActive = True
        self.haltonIndex = 1
        setAllNavigationsEnabled(0)
        self.placementStateChanged.emit(True)
        return True

    def stopPlacement(self):
        """Stop placement mode."""
        if not self.placementActive:
            return

        self.placementActive = False
        setAllNavigationsEnabled(1)
        self.placementStateChanged.emit(False)

    def togglePlacement(self):
        """Toggle placement mode on/off."""
        if self.placementActive:
            self.stopPlacement()
        else:
            return self.startPlacement()
        return True

    def isPlacementActive(self):
        """Check if placement mode is active."""
        return self.placementActive


class MouseListener(vrAEBase):
    """
    Mouse event listener for placement mode.
    Listens for left mouse button clicks when placement mode is active.
    """
    def __init__(self, scatterEngine):
        vrAEBase.__init__(self)
        self.scatterEngine = scatterEngine
        self.leftButtonState = 0x0
        self.addLoop()

    def loop(self):
        if (self.isActive() and self.scatterEngine.isPlacementActive() and 
            self.scatterEngine.sourceObjects):
            leftButtonPressed = ctypes.windll.user32.GetKeyState(LEFTCLICK)
            if leftButtonPressed != self.leftButtonState:
                self.leftButtonState = leftButtonPressed
                if self.leftButtonState > 1:
                    self.scatterEngine.placeClone()


class ScatterTool(ScatterTool_base, ScatterTool_form):
    """
    Main widget for the Scatter Tool plugin.
    Provides UI for configuring scatter settings and controlling placement mode.
    """
    def __init__(self, parent=None):
        super(ScatterTool, self).__init__(parent)
        parent.layout().addWidget(self)
        self.parent = parent
        self.setupUi(self)
        self._initialFitApplied = False

        # Apply SingleColumnButton style from Theme.qss to all buttons
        self.setSourceObjectsButton.setObjectName("SingleColumnButton")
        self.setTargetGroupButton.setObjectName("SingleColumnButton")
        self.clearTargetGroupButton.setObjectName("SingleColumnButton")
        self.resetSeedButton.setObjectName("SingleColumnButton")
        self.togglePlacementButton.setObjectName("SingleColumnButton")

        # Remove Window flag to embed into VRED plugin widget
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.Window)

        # Initialize settings and engine
        self.settings = ScatterSettings()
        self.scatterEngine = ScatterEngine(self.settings)
        self.mouseListener = MouseListener(self.scatterEngine)
        self.mouseListener.setActive(True)
        self.lastConfigFile = ""

        # Connect UI signals to handlers
        self.connectSignals()

        # Set up toolbar icons
        self.actionLoad.setIcon(getIcon("FileOpen"))
        self.actionSave.setIcon(getIcon("Save"))

        # Update UI to reflect initial settings
        self.updateUI()

        # Run once after first layout pass so initial plugin size fits content.
        QtCore.QTimer.singleShot(0, self.fitWindowToContentOnce)

    def connectSignals(self):
        """Connect all UI signals to their handlers."""
        # Scatter settings
        self.objectsPerClickSpinBox.valueChanged.connect(self.onObjectsPerClickChanged)
        self.scatterRadiusSpinBox.valueChanged.connect(self.onScatterRadiusChanged)
        self.distributionComboBox.currentTextChanged.connect(self.onDistributionChanged)

        # Rotation settings
        self.applyRandomRotationCheckBox.stateChanged.connect(self.onApplyRandomRotationChanged)

        # Scale settings
        self.applyRandomScaleCheckBox.stateChanged.connect(self.onApplyRandomScaleChanged)
        self.minimumScaleSpinBox.valueChanged.connect(self.onMinimumScaleSpinBoxChanged)
        self.maximumScaleSpinBox.valueChanged.connect(self.onMaximumScaleSpinBoxChanged)


        # Random settings
        self.seedLineEdit.editingFinished.connect(self.onSeedChanged)
        self.resetSeedButton.clicked.connect(self.onResetSeed)

        # Source objects and target group
        self.setSourceObjectsButton.clicked.connect(self.onSetSourceObjects)
        self.setTargetGroupButton.clicked.connect(self.onSetTargetGroup)
        self.clearTargetGroupButton.clicked.connect(self.onClearTargetGroup)

        # Placement mode
        self.togglePlacementButton.clicked.connect(self.onTogglePlacement)

        # Engine signals
        self.scatterEngine.placementStateChanged.connect(self.onPlacementStateChanged)
        self.scatterEngine.sourceObjectsChanged.connect(self.onSourceObjectsChanged)
        self.scatterEngine.targetGroupChanged.connect(self.onTargetGroupChanged)

        # Menu actions
        self.actionLoad.triggered.connect(self.onLoad)
        self.actionSave.triggered.connect(self.onSave)

        # Project loaded signal
        vrFileIOService.projectLoaded.connect(self.onProjectLoaded)

    def onObjectsPerClickChanged(self, value):
        self.settings.objectsPerClick = value

    def onScatterRadiusChanged(self, value):
        self.settings.scatterRadius = value

    def onDistributionChanged(self, value):
        self.settings.distributionMode = value

    def onApplyRandomRotationChanged(self, state):
        self.settings.applyRandomRotation = (state != 0)

    def onApplyRandomScaleChanged(self, state):
        self.settings.applyRandomScale = (state != 0)
        self.updateScaleWidgetsEnabled()

    def onMinimumScaleSpinBoxChanged(self, value):
        self.settings.minimumScaleSpinBox = value
        if value > self.settings.maximumScaleSpinBox:
            self.maximumScaleSpinBox.setValue(value)

    def onMaximumScaleSpinBoxChanged(self, value):
        self.settings.maximumScaleSpinBox = value
        if value < self.settings.minimumScaleSpinBox:
            self.minimumScaleSpinBox.setValue(value)

    def onSeedChanged(self):
        """Parse and update the seed value."""
        seedText = self.seedLineEdit.text().strip()
        try:
            # Try to parse as hex (0x prefix) or decimal
            if seedText.lower().startswith('0x'):
                self.settings.seed = int(seedText, 16)
            else:
                self.settings.seed = int(seedText)
        except ValueError:
            vrLogWarning("ScatterTool: Invalid seed value. Using default.")
            self.settings.seed = 0xfea1dab8
            self.seedLineEdit.setText("0xfea1dab8")

    def onResetSeed(self):
        """Reset the random number generator with the current seed."""
        self.onSeedChanged()  # Ensure seed is parsed
        self.scatterEngine.resetRandomSeed()

    def onTogglePlacement(self):
        """Toggle placement mode."""
        if self.scatterEngine.isPlacementActive():
            self.scatterEngine.stopPlacement()
        else:
            if not self.scatterEngine.startPlacement():
                self.togglePlacementButton.setChecked(False)

    def onPlacementStateChanged(self, active):
        """Update UI when placement state changes."""
        self.togglePlacementButton.setChecked(active)
        if active:
            self.togglePlacementButton.setText("Stop Scatter")
        else:
            self.togglePlacementButton.setText("Scatter")

    def onSetSourceObjects(self):
        """Handle Set Source Objects button click."""
        self.scatterEngine.setSourceObjects()

    def onSetTargetGroup(self):
        """Handle Set Target Group button click."""
        self.scatterEngine.setTargetGroup()

    def onClearTargetGroup(self):
        """Handle Clear Target Group button click."""
        self.scatterEngine.clearTargetGroup()

    def onSourceObjectsChanged(self):
        """Update UI when source objects change."""
        self.sourceObjectsValue.setText(self.scatterEngine.getSourceObjectNames())

    def onTargetGroupChanged(self):
        """Update UI when target group changes."""
        self.targetGroupValue.setText(self.scatterEngine.getTargetGroupName())

    def updateScaleWidgetsEnabled(self):
        """Enable/disable scale widgets based on checkbox state."""
        enabled = self.settings.applyRandomScale
        self.minimumScaleSpinBox.setEnabled(enabled)
        self.maximumScaleSpinBox.setEnabled(enabled)

    def updateUI(self):
        """Update all UI elements to reflect current settings."""
        # Block signals to prevent feedback loops
        self.objectsPerClickSpinBox.blockSignals(True)
        self.scatterRadiusSpinBox.blockSignals(True)
        self.distributionComboBox.blockSignals(True)
        self.applyRandomRotationCheckBox.blockSignals(True)
        self.applyRandomScaleCheckBox.blockSignals(True)
        self.minimumScaleSpinBox.blockSignals(True)
        self.maximumScaleSpinBox.blockSignals(True)
        self.seedLineEdit.blockSignals(True)

        # Update values
        self.objectsPerClickSpinBox.setValue(self.settings.objectsPerClick)
        self.scatterRadiusSpinBox.setValue(self.settings.scatterRadius)
        idx = self.distributionComboBox.findText(self.settings.distributionMode)
        if idx != -1:
            self.distributionComboBox.setCurrentIndex(idx)
        self.applyRandomRotationCheckBox.setChecked(self.settings.applyRandomRotation)
        self.applyRandomScaleCheckBox.setChecked(self.settings.applyRandomScale)
        self.minimumScaleSpinBox.setValue(self.settings.minimumScaleSpinBox)
        self.maximumScaleSpinBox.setValue(self.settings.maximumScaleSpinBox)
        self.seedLineEdit.setText(hex(self.settings.seed))

        # Unblock signals
        self.objectsPerClickSpinBox.blockSignals(False)
        self.scatterRadiusSpinBox.blockSignals(False)
        self.distributionComboBox.blockSignals(False)
        self.applyRandomRotationCheckBox.blockSignals(False)
        self.applyRandomScaleCheckBox.blockSignals(False)
        self.minimumScaleSpinBox.blockSignals(False)
        self.maximumScaleSpinBox.blockSignals(False)
        self.seedLineEdit.blockSignals(False)

        # Update dependent widget states
        self.updateScaleWidgetsEnabled()

    def showEvent(self, event):
        """Ensure initial size fit also runs when widget is shown."""
        super(ScatterTool, self).showEvent(event)
        self.fitWindowToContentOnce()

    def fitWindowToContentOnce(self):
        """
        Resize the plugin UI once on first show so scrollbars are not visible initially.
        The user can still manually resize smaller later and get scrollbars as needed.
        """
        if self._initialFitApplied:
            return
        if not hasattr(self, "mainScrollArea") or not hasattr(self, "scrollAreaWidgetContents"):
            return

        self.scrollAreaWidgetContents.adjustSize()
        contentSize = self.scrollAreaWidgetContents.sizeHint()
        framePadding = 2 * self.mainScrollArea.frameWidth()
        targetWidth = max(self.width(), contentSize.width() + framePadding)
        targetHeight = max(self.height(), contentSize.height() + framePadding)

        menu_bar = getattr(self, "menuBar", None)
        if menu_bar is not None and hasattr(menu_bar, "sizeHint"):
            targetHeight += menu_bar.sizeHint().height()

        self.resize(targetWidth, targetHeight)

        # If embedded in a parent container, grow that container as well.
        if self.parent is not None and hasattr(self.parent, "resize"):
            parentWidth = max(self.parent.width(), targetWidth)
            parentHeight = max(self.parent.height(), targetHeight)
            self.parent.resize(parentWidth, parentHeight)

        self._initialFitApplied = True

    def onLoad(self):
        """Load settings from a file."""
        configFile = QFileDialog.getOpenFileName(None, "Load Scatter Settings", "", "JSON Files (*.json);;All Files (*)")[0]
        if len(configFile) > 0:
            self.loadConfig(configFile)

    def onSave(self):
        """Save settings to a file."""
        configFile = QFileDialog.getSaveFileName(None, "Save Scatter Settings", self.getSuggestedFilename(), "JSON Files (*.json);;All Files (*)")[0]
        if len(configFile) > 0:
            self.saveConfig(configFile)

    def getSuggestedFilename(self):
        """Suggest a filename for saving settings."""
        suggestedFilename = "scatter_settings.json"
        vredFile = vrFileIOService.getFileName()
        filepath, ext = os.path.splitext(vredFile)
        if ext == ".vpb":
            suggestedFilename = filepath + "_scatter.json"
        elif self.lastConfigFile:
            suggestedFilename = self.lastConfigFile
        return suggestedFilename

    def onProjectLoaded(self, file):
        """Auto-load scatter settings file if it exists next to the loaded .vpb file."""
        filepath, ext = os.path.splitext(file)
        if ext == ".vpb":
            configFile = filepath + "_scatter.json"
            if os.path.exists(configFile):
                self.loadConfig(configFile)

    def saveConfig(self, fileName):
        """Save settings to a JSON file."""
        try:
            with open(fileName, 'w') as f:
                json.dump(self.settings.toDict(), f, indent=2)
            self.lastConfigFile = fileName
        except IOError as e:
            vrLogError("ScatterTool: Could not save {}. I/O error({}): {}".format(fileName, e.errno, str(e)))
        except Exception as e:
            vrLogError("ScatterTool: Could not save {}. Error: {}".format(fileName, str(e)))

    def loadConfig(self, fileName):
        """Load settings from a JSON file."""
        if os.path.exists(fileName):
            try:
                with open(fileName, 'r') as f:
                    data = json.load(f)
                self.settings.fromDict(data)
                self.lastConfigFile = fileName
                self.updateUI()
                self.scatterEngine.resetRandomSeed()
            except IOError as e:
                vrLogError("ScatterTool: Could not load {}. I/O error({}): {}".format(fileName, e.errno, str(e)))
            except json.JSONDecodeError as e:
                vrLogError("ScatterTool: Could not parse {}. JSON error: {}".format(fileName, str(e)))
            except Exception as e:
                vrLogError("ScatterTool: Could not load {}. Error: {}".format(fileName, str(e)))


# Global variable for plugin
scatterPlugin = None


def onDestroyVREDScriptPlugin():
    """
    onDestroyVREDScriptPlugin() is called before this plugin is destroyed.
    Stop placement mode and clean up.
    """
    if scatterPlugin is not None:
        scatterPlugin.scatterEngine.stopPlacement()
        scatterPlugin.mouseListener.setActive(False)


# Create the plugin widget
try:
    scatterPlugin = ScatterTool(VREDPluginWidget)
except Exception as e:
    print("ScatterTool: Error initializing plugin: {}".format(str(e)))
    import traceback
    traceback.print_exc()
