# textureAnimation
# source: textureAnimation.html

# © 2026 Autodesk, Inc. All rights reserved.

texSwitch = findNode("TimedTextureSwitch")
textureDir = "C:/DummyTextures/"
textureName = "alwaysRebuild"
textureExt = "jpg"
currentChoice = 1

def replaceImage():
    global currentChoice
    activeChoice = texSwitch.fields().getInt32("choice")
    if activeChoice != currentChoice:
        currentName = "%s%s%05d.%s" % (textureDir, textureName, activeChoice, textureExt)
        setMaterialImage(findMaterial("lightMat"), "incandescenceMap", currentName)
        currentChoice = activeChoice

timer = vrTimer()
timer.connect(replaceImage)
timer.setActive(true)
