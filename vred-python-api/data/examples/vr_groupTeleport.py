# Extend the default teleport to multi user teleport
# source: groupTeleport.html

self.leftConstraint = vrConstraintService.createParentConstraint([self.leftController.getNode()], self.leftDisk, True)
self.rightConstraint = vrConstraintService.createParentConstraint([self.rightController.getNode()], self.rightDisk, True)

cameraNode = vrCameraService.getActiveCamera()
vrSessionService.syncNode(cameraNode)

# © 2026 Autodesk, Inc. All rights reserved.

# Class for the group teleport
class GroupTeleport:
    def __init__(self):        
        self.isActive = False        
        self.setupButtons()
        self.setupInteraction()
        self.setupVisualization()           

    def setupButtons(self):
        # Create touchpad layout. Upper half of pad is one button ...
        self.padUp = vrdVirtualTouchpadButton("padup", 0.0, 1.0, 270.0, 90.0)
        # ... and the lower half is another button
        self.padDown = vrdVirtualTouchpadButton("paddown", 0.0, 1.0, 90.0, 270.0)

        # Get the controllers
        self.leftController = vrDeviceService.getVRDevice("left-controller")
        self.rightController = vrDeviceService.getVRDevice("right-controller")

        # Assign the virtual touchpad buttons to the left ...
        self.leftController.addVirtualButton(self.padUp, "Touchpad")
        self.leftController.addVirtualButton(self.padDown, "Touchpad")
        # ... and to the right controller
        self.rightController.addVirtualButton(self.padUp, "Touchpad")
        self.rightController.addVirtualButton(self.padDown, "Touchpad")

        # Map the default teleport interaction top the lower button
        self.teleportInteraction = vrDeviceService.getInteraction("Teleport")
        self.teleportInteraction.setControllerActionMapping("prepare", "any-paddown-touched")
        self.teleportInteraction.setControllerActionMapping("execute", "any-paddown-pressed")
        self.teleportInteraction.setControllerActionMapping("abort", "any-paddown-untouched")

    def setupInteraction(self):
        # Create an interaction for the group teleport
        self.groupTeleportInteraction = vrDeviceService.createInteraction("GroupTeleport")

        # Map the toggle active to the upper pad button
        self.beginToggleAction = self.groupTeleportInteraction.createControllerAction("any-padup-pressed")
        self.toggleActiveAction = self.groupTeleportInteraction.createControllerAction("any-padup-released")        
        # Get the execute action of the teleport
        self.teleportExecuteAction = self.teleportInteraction.getControllerAction("execute")
        # Map the pad down for some visual indicators
        self.teleportExecuteFinishedAction = self.groupTeleportInteraction.createControllerAction("any-paddown-released")

        # Connect the signals
        self.beginToggleAction.signal().triggered.connect(self.beginToggle)
        self.toggleActiveAction.signal().triggered.connect(self.toggleActive)
        self.teleportExecuteAction.signal().triggered.connect(self.execute)
        self.teleportExecuteFinishedAction.signal().triggered.connect(self.executeFinished)

    def setupVisualization(self):
        # Load geometry for controller touchpads
        loadGeometry("$VRED_EXAMPLES/vr/GroupTeleportPad.osb")
        # Find the touchpad geometry in the scene that shows the virtual buttons
        oldLeftDisk = findNode("ControllerDisk")        

        # Create a lookup for the different visualization states
        self.diskVisualizations = dict()

        # Check if the touchpad geometry has been found
        if oldLeftDisk.isValid():
            # Geometry is also needed for the right controller, therefore clone it
            oldRightDisk = cloneNode(oldLeftDisk, False)
            # Convert to new vrdNode
            self.leftDisk = vrNodeService.getNodeFromId(oldLeftDisk.getID())
            self.rightDisk = vrNodeService.getNodeFromId(oldRightDisk.getID())
            
            # Setup all touchpad geometries for the left hand            
            self.diskVisualizations["leftSingle"] = self.leftDisk.getChild(0)
            self.diskVisualizations["leftGroup"] = self.leftDisk.getChild(1)
            self.diskVisualizations["leftUp"] = self.leftDisk.getChild(2)
            self.diskVisualizations["leftSingleDown"] = self.leftDisk.getChild(3)
            self.diskVisualizations["leftGroupDown"] = self.leftDisk.getChild(4)

            # Setup all touchpad geometries for the right hand
            self.diskVisualizations["rightSingle"] = self.rightDisk.getChild(0)
            self.diskVisualizations["rightGroup"] = self.rightDisk.getChild(1)
            self.diskVisualizations["rightUp"] = self.rightDisk.getChild(2)
            self.diskVisualizations["rightSingleDown"] = self.rightDisk.getChild(3)
            self.diskVisualizations["rightGroupDown"] = self.rightDisk.getChild(4)

            # Use a constraint to position the touchpad geometry correctly
            self.leftConstraint = vrConstraintService.createParentConstraint([self.leftController.getNode()], self.leftDisk, True)
            self.rightConstraint = vrConstraintService.createParentConstraint([self.rightController.getNode()], self.rightDisk, True)            

            self.initialized = True
        else:
            self.initialized = False

        # Set the visualization of the devices to controller instead of hands
        self.leftController.setVisualizationMode(0)
        self.rightController.setVisualizationMode(0)

        # Set the visualization state of the touchpad disk
        self.showSingleDisk()
    
    def toggleActive(self, action, device):    
        self.isActive = not self.isActive
        if self.isActive:            
            # Show the touchpad geometry used for group teleport
            self.showGroupDisk()
        else:            
            # Show the touchpad geometry used for regular teleport
            self.showSingleDisk()


    def beginToggle(self, action, device):
        left = True
        # Check if the right or the left controller triggered this
        if 'right' in device.getName():
            left = False
        # Highlights the upper button
        self.showDiskUp(left)


    def execute(self, action, device):
        left = True
        # Check if the right or the left controller triggered this
        if 'right' in device.getName():
            left = False

        # Highlight the lower button
        self.showDiskDown(left)

        # If inactive just return as the regular teleport will work as usual
        if not self.isActive:
            return        

        # Sync the active camera with all participants in the session to teleport them, too.
        cameraNode = vrCameraService.getActiveCamera()
        vrSessionService.syncNode(cameraNode)


    def executeFinished(self, action, device):
        if self.isActive:
            # Show 'Group' on the upper button
            self.showGroupDisk()
        else:
            # Show 'Single' on the upper button
            self.showSingleDisk()


    def hideAllDisks(self):
        if not self.initialized:
            return

        # Iterate over the lookup to set all geometries to invisible
        for name, disk in self.diskVisualizations.items():
            disk.setVisibilityFlag(False)


    def hideDisksOneSided(self, left):
        if not self.initialized:
            return

        side = 'right'
        if left:
            side = 'left'

        # Iterate over the lookup to set all geometries of one side to invisible
        for name, disk in self.diskVisualizations.items():
            if side in name:
                disk.setVisibilityFlag(False)


    def showGroupDisk(self):
        if not self.initialized:
            return

        # Hide all touchpad geometries first to ensure only the correct ones will be shown.
        self.hideAllDisks()
        # Show the touchpad geometry with 'Group' on the upper button.
        # Do this for both sides as this state is for both hands
        self.diskVisualizations["leftGroup"].setVisibilityFlag(True)
        self.diskVisualizations["rightGroup"].setVisibilityFlag(True)


    def showSingleDisk(self):
        if not self.initialized:
            return

        # Hide all touchpad geometries first to ensure only the correct ones will be shown.
        self.hideAllDisks()
        # Show the touchpad geometry with 'Single' on the upper button.
        # Do this for both sides as this state is for both hands
        self.diskVisualizations["leftSingle"].setVisibilityFlag(True)
        self.diskVisualizations["rightSingle"].setVisibilityFlag(True)


    def showDiskUp(self, left):
        if not self.initialized:
            return

        # Hide all touchpad geometries for the given side first to ensure only the correct ones will be shown.
        self.hideDisksOneSided(left)

        # Show the highlighted geometry for the lower button for the given hand.
        if left:            
            self.diskVisualizations["leftUp"].setVisibilityFlag(True)
        else:            
            self.diskVisualizations["rightUp"].setVisibilityFlag(True)


    def showDiskDown(self, left):
        if not self.initialized:
            return

        # Hide all touchpad geometries for the given side first to ensure only the correct ones will be shown.
        self.hideDisksOneSided(left)

        # Show the highlighted geometry for the upper button for the given hand
        # It also needs to be distinhuished which mode is currently active to show the correct highlighted geometry.        
        if left:
            if self.isActive:
                self.diskVisualizations["leftGroupDown"].setVisibilityFlag(True)
            else:
                self.diskVisualizations["leftSingleDown"].setVisibilityFlag(True)
        else:
            if self.isActive:
                self.diskVisualizations["rightGroupDown"].setVisibilityFlag(True)
            else:
                self.diskVisualizations["rightSingleDown"].setVisibilityFlag(True)
    

groupTeleport = GroupTeleport()
