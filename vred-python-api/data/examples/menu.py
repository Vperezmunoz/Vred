# Menu with buttons and checkboxes example 1
# source: menu.html

# © 2026 Autodesk, Inc. All rights reserved.

print("Executing demo script!")

newScene()

loadGeometry("$VRED_EXAMPLES/geo/car.osb")
loadGeometry("$VRED_EXAMPLES/geo/teddy.osb")

updateScene()
calcVertexNormals()

teddy = findNode("Teddy_Bear", True);
teddy.makeTransform()

axis = createLine(0,0,0,0,0,1,0,0,0)
hideNode(axis)

# define interpolator that will be activated over a menu entry
cubeInt = vrInterpolator()
cubeSlide = vrRotationAxisSlide(teddy, axis, 0, 359, 8.0)
cubeInt.add(cubeSlide)

# define menu with entries and respective functions to be called
menu1 = vrMenu(0.05, 1, 1)
menu1.setTransform(-1.5, 0, -10, 0, 45 , 0)
menu1.addLabel("<font color=red>Menu</font>")
menu1.addCheckBox("Rotate teddy", cubeInt)
menu1.addCheckBox("Show scenegraph", "showScenegraph(item_state)")
menu1.addPushButton("Update Scene", "updateScene()")
menu1.setAlpha(0.3)

timer = vrTimer(0.2, true)
timer.setActive(true)
timer.connect("menu1.show()")

print("Press Shift and click onto each menu entry")
