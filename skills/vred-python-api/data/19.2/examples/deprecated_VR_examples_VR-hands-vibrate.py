# (Deprecated) Use vibration on touch
# source: VR-hands-vibrate.html

# © 2026 Autodesk, Inc. All rights reserved.

class OculusVibration:
    
    def __init__(self, controller):
        self.controller = controller

    def stopVibration(self):
        self.controller.triggerVibration(0.0, 0.0)
        self.timer = None

    def vibrate(self, frequency, amplitude, seconds):
        # timer to stop the vibration
        self.timer = vrTimer()
        self.timer.setSingleShot(True)
        self.timer.connect(self.stopVibration)
        self.timer.setInterval(seconds)
        self.timer.setActive(True)
        # start vibration
        self.controller.triggerVibration(frequency, amplitude)
        
    def strongPulse(self):
        frequency = 0.0 # 160 Hz
        amplitude = 0.1
        seconds = 0.1
        self.vibrate(frequency, amplitude, seconds)
        
    def weakPulse(self):
        frequency = 0.0 # 160 Hz
        amplitude = 0.1
        seconds = 0.05
        self.vibrate(frequency, amplitude, seconds)
    

handRoleString = { Hand_Left : "Left", Hand_Right : "Right" }

def handTouchStarted(touchedNodeId, fingerId, vibration):
    print("handTouchStarted on controller {}, finger {}".format(handRoleString[vibration.controller.getHandRole()], str(fingerId)))
    vibration.strongPulse()

def handTouchStopped(touchedNodeId, fingerId, vibration):
    print("handTouchStopped on controller {}, finger {}".format(handRoleString[vibration.controller.getHandRole()], str(fingerId)))
    vibration.weakPulse()

# Deprecated class vrOculusTouchController. See vrDeviceService, vrdVRDevice, vrdDeviceInteraction instead.
leftController = vrOculusTouchController("LeftTouch")
leftController.setVisible(True)
leftVib = OculusVibration(leftController)

leftController.connectSignal("handTouchStarted", handTouchStarted, leftVib)
leftController.connectSignal("handTouchStopped", handTouchStopped, leftVib)

rightController = vrOculusTouchController("RightTouch")
rightController.setVisible(True)
rightVib = OculusVibration(rightController)

rightController.connectSignal("handTouchStarted", handTouchStarted, rightVib)
rightController.connectSignal("handTouchStopped", handTouchStopped, rightVib)

# © 2026 Autodesk, Inc. All rights reserved.

handRoleString = { Hand_Left : "Left", Hand_Right : "Right" }

def handTouchStarted(touchedNodeId, fingerId, controller):
    print("handTouchStarted on controller {}, finger {}".format(handRoleString[controller.getHandRole()], str(fingerId)))
    controller.triggerHapticPulse(0,1000)

def handTouchStopped(touchedNodeId, fingerId, controller):
    print("handTouchStopped on controller {}, finger {}".format(handRoleString[controller.getHandRole()], str(fingerId)))
    controller.triggerHapticPulse(0,300)

# Deprecated class vrOpenVRController. See vrDeviceService, vrdVRDevice, vrdDeviceInteraction instead.
controller0 = vrOpenVRController("Controller0")
controller1 = vrOpenVRController("Controller1")
controller0.setVisualizationMode(Visualization_Hand)
controller1.setVisualizationMode(Visualization_Hand)

controller0.connectSignal("handTouchStarted", handTouchStarted, controller0)
controller1.connectSignal("handTouchStarted", handTouchStarted, controller1)
controller0.connectSignal("handTouchStopped", handTouchStopped, controller0)
controller1.connectSignal("handTouchStopped", handTouchStopped, controller1)
