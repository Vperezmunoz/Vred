# Menu mapped on a cube
# source: menu3d_scene.html

# © 2026 Autodesk, Inc. All rights reserved.

obj = createBox(1000, 1000, 1000, 1, 1, 1, 0, 0, 0)
#obj = createPlane(1280, 720, 1, 1, 0, 0, 0)

trans = createNode('Transform3D', 'rotate')
trans.setRotation(90, 0, 0)
trans.addChild(obj)

menu = vrMenu(1, 1, 1)
menu.setNode(obj)
menu.setWindowResize("Transform", 640, 400)

menu.show()
