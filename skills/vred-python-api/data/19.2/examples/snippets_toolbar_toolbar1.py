# A toolbar icon with a single action
# source: toolbar1.html

# © 2026 Autodesk, Inc. All rights reserved.

# This example shows how to add a custom icon to the VRED Toolbar.
# It creates a toolbar with a single action that prints a message to the console when clicked.
# The toolbar is also added as a toggle to the View->Toolbars menu.

from PySide6 import QtGui, QtWidgets
import datetime, os

def my_tool_action():
    print(f"My Tool: {datetime.datetime.now()}.")

exampleFolder = os.path.join(os.getenv('VRED_ROOT'), "examples", "snippets", "toolbar")
iconPath = os.path.join(exampleFolder, "my_tool_icon.png")

my_action = QtGui.QAction(QIcon(iconPath), 'My Tool')
my_action.setToolTip('My Tool\n\nClick to activate.')
my_action.triggered.connect(my_tool_action)

my_toolbar = QtWidgets.QToolBar('my_toolbar')
my_toolbar.setToolButtonStyle(QtGui.Qt.ToolButtonTextUnderIcon)
my_toolbar.addAction(my_action)
vrGUIService.addMainWindowToolBar(my_toolbar)
