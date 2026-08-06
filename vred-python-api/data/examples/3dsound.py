# 3D sound examples
# source: 3dsound.html

# © 2026 Autodesk, Inc. All rights reserved.

newScene()
loadGeometry("$VRED_EXAMPLES/geo/sound.osb")
updateScene()

hideNode(findNode("Environments"))

vrLogInfo("On the red objects position you hear a beating sound.")
vrLogInfo("On the green objects position you hear a diesel engine sound.")

# find node and convert it into transformation node
rot = findNode("Rotate");
rot.makeTransform()

# define 360 degree rotation and activate it
rotInt = vrInterpolator()
rotSlide = vrRotationSlide(rot, 0,0,0, 0,359,0, 8.0)
rotInt.add(rotSlide)
rotInt.setActive(true)

#define key r to toggle rotation
keyR = vrKey(Key_R)
keyR.connect(rotInt, SWITCH_TOGGLE)
vrLogInfo("Press key r to toggle rotation")

# © 2026 Autodesk, Inc. All rights reserved.
newScene()

sound = vrScenegraphService.createNode(vrScenegraphTypes.SoundNode)
sound.setName("Sound")
filename = "$VRED_EXAMPLES/audio/motor_b8.wav"
sound.setSoundFile(filename)

def play(s):
    sound.setPlay(s)

def pitch(v):
    sound.setPitch(v)

keyP = vrKey(Key_P)
keyP.connect(play, true)

keyS = vrKey(Key_S)
keyS.connect(play, false)

keyH = vrKey(Key_H)
keyH.connect(pitch, 2.0)

keyL = vrKey(Key_J)
keyL.connect(pitch, 0.5)

keyR = vrKey(Key_R)
keyR.connect(pitch, 1.0)

vrLogInfo("Press key 'p' to play")
vrLogInfo("Press key 's' to stop")
vrLogInfo("Press key 'h' increase pitch")
vrLogInfo("Press key 'j' decrease pitch")
vrLogInfo("Press key 'r' reset pitch")
