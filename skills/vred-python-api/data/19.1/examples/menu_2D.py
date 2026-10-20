# Menu with buttons and checkboxes example 2
# source: menu_2D.html

# © 2026 Autodesk, Inc. All rights reserved.

def hello():
    print("Hello World!")

menu1 = vrMenu(2, 1, 1)
menu1.setPosition2D(10,10)
menu1.addLabel("<font color=red>Menu</font>")
menu1.addCheckBox("Show statistics", "showStatistic(item_state)")
menu1.addPushButton("Hello World", "hello()")
menu1.setAlpha(1)
menu1.show()
