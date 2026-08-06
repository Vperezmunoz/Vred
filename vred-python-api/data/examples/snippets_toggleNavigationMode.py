# toggleNavigationMode
# source: toggleNavigationMode.html

# © 2026 Autodesk, Inc. All rights reserved.

#initialize the nav mode
currentNavMode = 3
#small procedure to toggle between nav mode 3 and 4
def toggleNav():
    global currentNavMode
    if currentNavMode == 4:
        setNavMode(3)
        currentNavMode = 3
    else:
        setNavMode(4)
        currentNavMode = 4

#bind to key n
KeyOrientation = vrKey(Key_N)
KeyOrientation.connect("toggleNav()")
