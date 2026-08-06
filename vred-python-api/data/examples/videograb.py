# video grabbing example
# source: videograb.html

# © 2026 Autodesk, Inc. All rights reserved.

screen = createPlane(2000, 1000, 1, 1, 0,0,0)
screen.setRotation(90,0,0)
screen.setTranslation(0, 0, 500)

vg = vrVideoGrab(screen, "LifeView")
# specify a resolution.
#vg = vrVideoGrab(curve, "LifeView", 768, 576)
vg.setActive(true)

# define key s to toggle videograbbing
keyS = vrKey(Key_S)
keyS.connect(vg, SWITCH_TOGGLE)
vrLogInfo("Press key s to toggle videograbbing")
