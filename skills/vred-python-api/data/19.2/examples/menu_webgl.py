# Menu with a WebGL demo
# source: menu_webgl.html

# © 2026 Autodesk, Inc. All rights reserved.

box = createBox(1000, 1000, 1000, 1, 1, 1, 1, 1, 1)

menu = vrMenu(1,1,1)
menu.setPosition2D(10,10)
menu.setAutoResize(0.0010)
menu.setUrl("http://webglsamples.org/electricflower/electricflower.html")
#menu.setUrl("http://webglsamples.org/fishtank/fishtank.html")
menu.setAlpha(0.5)
menu.show()
